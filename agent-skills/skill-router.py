#!/usr/bin/env python3
"""Resolve a deterministic, explainable Agent Skill set from text, events, and project facts."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Sequence

ROUTING_FILE = Path(__file__).with_name("skill-routing.json")
REGRESSION_FILE = Path(__file__).with_name("route-regression.json")
REPOSITORY_ROOT = Path(__file__).parent.parent
LEVEL_ORDER = {"P1": 0, "P2": 1, "P3": 2}
TOKEN_PATTERN = re.compile(r"c#|\.net|[a-z][a-z0-9#+.-]*|[0-9]+(?:\.[0-9]+)+|[\u3400-\u9fff]+")


def tokenize(text: str) -> list[str]:
    """Return stable technology and CJK tokens from arbitrary task text."""
    return TOKEN_PATTERN.findall(text.lower())


def normalize_tokens(tokens: Iterable[str], routing: dict) -> list[str]:
    aliases = routing.get("normalize", {}).get("aliases", {})
    return [aliases.get(token, token) for token in tokens]


def _contains_sequence(tokens: Sequence[str], phrase: Sequence[str]) -> bool:
    if not phrase or len(phrase) > len(tokens):
        return False
    width = len(phrase)
    return any(list(tokens[index : index + width]) == list(phrase) for index in range(len(tokens) - width + 1))


def detect_project_facts(project_root: Path | None) -> list[str]:
    """Detect conservative language and workspace facts without modifying the project."""
    if project_root is None:
        return []
    root = project_root.resolve()
    if not root.is_dir():
        return []

    facts: set[str] = set()

    def exists(name: str) -> bool:
        return (root / name).exists()

    if any(exists(name) for name in ("pyproject.toml", "setup.py", "setup.cfg", "uv.lock", "requirements.txt")):
        facts.add("python")
    if exists("go.mod") or exists("go.work"):
        facts.add("go")
    if exists("Cargo.toml"):
        facts.add("rust")
    if exists("package.json") or exists("tsconfig.json") or exists("jsconfig.json"):
        facts.add("javascript-typescript")
    if exists("tsconfig.json") or list(root.glob("tsconfig.*.json")):
        facts.update(("javascript-typescript", "typescript"))
    cmake = root / "CMakeLists.txt"
    if cmake.is_file():
        try:
            cmake_text = re.sub(r"#\[(=*)\[.*?\]\1\]", "", cmake.read_text(encoding="utf-8"), flags=re.DOTALL)
            cmake_text = re.sub(r"#[^\n]*", "", cmake_text)
            # Ignore string payloads and bracket arguments: a description or
            # project name containing CXX is not a language declaration.
            cmake_text = re.sub(r'"(?:\\.|[^"\\])*"|\[(=*)\[.*?\]\1\]', '""', cmake_text, flags=re.DOTALL)
            for command in re.finditer(r"\b(project|enable_language)\s*\(([^)]*)\)", cmake_text, re.IGNORECASE):
                arguments = command[2].split()
                if command[1].lower() == "project":
                    # Explicit LANGUAGES only; unresolved variables and default
                    # languages do not provide enough evidence for this router.
                    if "LANGUAGES" not in arguments[1:]:
                        continue
                    arguments = arguments[arguments.index("LANGUAGES", 1) + 1:]
                    for index, argument in enumerate(arguments):
                        if argument in {"VERSION", "DESCRIPTION", "HOMEPAGE_URL"}:
                            arguments = arguments[:index]
                            break
                if "CXX" in arguments:
                    facts.add("cpp")
        except (OSError, UnicodeError):
            pass
    if exists("pom.xml") or exists("build.gradle") or exists("build.gradle.kts"):
        facts.add("java")
    if list(root.glob("*.sln")) or list(root.glob("*.slnx")) or list(root.glob("*.csproj")) or exists("Directory.Build.props"):
        facts.add("dotnet")
    if exists("AndroidManifest.xml") or list(root.glob("*/src/main/AndroidManifest.xml")):
        facts.add("android")
    if list(root.glob("*.xcodeproj")) or list(root.glob("*.xcworkspace")):
        facts.add("ios")
    if exists("pnpm-workspace.yaml") or exists("nx.json") or exists("turbo.json") or exists("go.work"):
        facts.add("monorepo")

    package_json = root / "package.json"
    if package_json.is_file():
        try:
            package = json.loads(package_json.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError):
            package = {}
        if not isinstance(package, dict):
            package = {}
        if package.get("workspaces"):
            facts.add("monorepo")
        dependencies = {}
        for key in ("dependencies", "devDependencies"):
            values = package.get(key, {})
            if isinstance(values, dict):
                dependencies.update(values)
        if "typescript" in dependencies:
            facts.add("typescript")
        if "vue" in dependencies or "nuxt" in dependencies:
            facts.update(("vue", "frontend"))
        if "react" in dependencies:
            facts.add("react")
            facts.add("frontend")

    cargo_toml = root / "Cargo.toml"
    if cargo_toml.is_file():
        try:
            if re.search(r"(?m)^\s*\[workspace\]\s*$", cargo_toml.read_text(encoding="utf-8")):
                facts.add("monorepo")
        except OSError:
            pass

    manifest_count = 0
    for pattern in ("*/pyproject.toml", "*/go.mod", "*/Cargo.toml", "*/package.json", "*/pom.xml", "*/*.csproj"):
        manifest_count += sum(1 for _ in root.glob(pattern))
    if manifest_count > 1:
        facts.add("monorepo")

    return sorted(facts)


def _add_reason(reasons: dict[str, list[str]], skill_name: str, reason: str) -> None:
    if reason not in reasons[skill_name]:
        reasons[skill_name].append(reason)


def resolve_skills(
    text: str,
    routing: dict,
    *,
    events: Iterable[str] = (),
    project_root: Path | None = None,
    files: Iterable[str] = (),
) -> dict:
    raw_tokens = tokenize(text)
    normalized_tokens = normalize_tokens(raw_tokens, routing)
    normalized_set = set(normalized_tokens)
    selected: set[str] = set()
    reasons: dict[str, list[str]] = defaultdict(list)
    matched_keywords: list[str] = []
    event_list = list(dict.fromkeys(events))
    target_files = list(dict.fromkeys(str(path).replace("\\", "/") for path in files))
    # Explicit targets scope language/framework loading; do not preload every
    # technology installed in an unrelated package or monorepo root.
    facts = detect_project_facts(project_root) if not target_files else []
    fact_set = set(facts)

    for skill_name, definition in routing.get("skills", {}).items():
        triggers = definition.get("triggers", {})
        for pattern in triggers.get("file_patterns", []):
            for target in target_files:
                if fnmatch.fnmatchcase(target, pattern):
                    selected.add(skill_name)
                    _add_reason(reasons, skill_name, f"file:{target}")
        for keyword in triggers.get("keywords", []):
            if keyword in normalized_set:
                selected.add(skill_name)
                _add_reason(reasons, skill_name, f"keyword:{keyword}")
                if keyword not in matched_keywords:
                    matched_keywords.append(keyword)
        for phrase in triggers.get("phrases", []):
            phrase_tokens = normalize_tokens(tokenize(phrase), routing)
            has_cjk = bool(re.search(r"[\u3400-\u9fff]", phrase))
            matched_phrase = phrase.lower() in text.lower() if has_cjk else _contains_sequence(normalized_tokens, phrase_tokens)
            if matched_phrase:
                selected.add(skill_name)
                _add_reason(reasons, skill_name, f"phrase:{phrase}")
        for event in triggers.get("events", []):
            if event in event_list:
                selected.add(skill_name)
                _add_reason(reasons, skill_name, f"event:{event}")
        for fact in triggers.get("project_facts", []):
            if fact in fact_set:
                selected.add(skill_name)
                _add_reason(reasons, skill_name, f"project-fact:{fact}")

    for rule in routing.get("combinations", []):
        when = rule.get("when_keywords", [])
        if all(keyword in normalized_set for keyword in when):
            for skill_name in rule.get("includes", []):
                selected.add(skill_name)
                _add_reason(reasons, skill_name, f"combination:{'+'.join(when)}")

    skills = routing.get("skills", {})

    def add_requirements(skill_name: str, chain: tuple[str, ...] = ()) -> None:
        if skill_name in chain:
            return
        for required in skills.get(skill_name, {}).get("requires", []):
            if required not in selected:
                selected.add(required)
                _add_reason(reasons, required, f"required-by:{skill_name}")
            add_requirements(required, chain + (skill_name,))

    for skill_name in list(selected):
        add_requirements(skill_name)

    warnings: list[str] = []
    for skill_name in sorted(list(selected)):
        if skill_name not in selected:
            continue
        for conflict in skills.get(skill_name, {}).get("conflicts", []):
            if conflict not in selected:
                continue
            left = skills[skill_name]
            right = skills[conflict]
            left_key = (LEVEL_ORDER.get(left.get("level"), 99), left.get("priority", 100000), skill_name)
            right_key = (LEVEL_ORDER.get(right.get("level"), 99), right.get("priority", 100000), conflict)
            loser = conflict if left_key <= right_key else skill_name
            winner = skill_name if loser == conflict else conflict
            selected.discard(loser)
            warnings.append(f"conflict:{winner} selected over {loser}")

    ordered = sorted(
        selected,
        key=lambda name: (
            LEVEL_ORDER.get(skills[name].get("level"), 99),
            skills[name].get("priority", 100000),
            name,
        ),
    )
    return {
        "query": text,
        "tokens": raw_tokens,
        "keywords": matched_keywords,
        "events": event_list,
        "project_facts": facts,
        "target_files": target_files,
        "skills": ordered,
        "files": [skills[name]["path"] for name in ordered],
        "reasons": {name: reasons[name] for name in ordered},
        "warnings": warnings,
    }


def parse_frontmatter(path: Path) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        return {}, [f"cannot read {path}: {exc}"]
    if not lines or lines[0].strip() != "---":
        return {}, [f"missing YAML frontmatter: {path}"]
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}, [f"unterminated YAML frontmatter: {path}"]
    data: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip() or line.startswith(" ") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip().strip('"\'')
    for required in ("name", "description"):
        if not data.get(required):
            errors.append(f"frontmatter missing {required}: {path}")
    return data, errors


def validate_routing(routing: dict, repository_root: Path = REPOSITORY_ROOT) -> list[str]:
    errors: list[str] = []
    if routing.get("schema") != "agent-skill-routing-v3":
        errors.append("schema must be agent-skill-routing-v3")

    skills = routing.get("skills")
    if not isinstance(skills, dict) or not skills:
        return errors + ["skills must be a non-empty object"]

    known_events = set(routing.get("events", []))
    seen_paths: dict[str, str] = {}
    seen_frontmatter_names: dict[str, str] = {}

    for skill_name, definition in skills.items():
        if not re.fullmatch(r"[a-z0-9-]{1,64}", skill_name):
            errors.append(f"invalid skill name: {skill_name}")
        path_text = definition.get("path")
        if not path_text:
            errors.append(f"{skill_name} has no path")
            continue
        if path_text in seen_paths:
            errors.append(f"duplicate skill path: {path_text} ({seen_paths[path_text]}, {skill_name})")
        seen_paths[path_text] = skill_name
        path = repository_root / path_text
        if not path.is_file():
            errors.append(f"{skill_name} references missing file: {path_text}")
            continue
        frontmatter, frontmatter_errors = parse_frontmatter(path)
        errors.extend(frontmatter_errors)
        if frontmatter.get("name") and frontmatter["name"] != skill_name:
            errors.append(f"frontmatter name mismatch: {path_text} declares {frontmatter['name']} not {skill_name}")
        if path.parent.name != skill_name:
            errors.append(f"skill folder mismatch: {path_text} must be inside {skill_name}/")
        declared_name = frontmatter.get("name")
        if declared_name:
            if declared_name in seen_frontmatter_names:
                errors.append(f"duplicate frontmatter name: {declared_name}")
            seen_frontmatter_names[declared_name] = path_text
        if definition.get("level") not in LEVEL_ORDER:
            errors.append(f"{skill_name} has invalid level: {definition.get('level')}")
        if not isinstance(definition.get("priority"), int):
            errors.append(f"{skill_name} must have an integer priority")
        if not definition.get("compatibility"):
            errors.append(f"{skill_name} has no compatibility hosts")
        triggers = definition.get("triggers", {})
        patterns = triggers.get("file_patterns", [])
        if not isinstance(patterns, list) or any(not isinstance(pattern, str) or not pattern for pattern in patterns):
            errors.append(f"{skill_name} file_patterns must be a list of non-empty strings")
        for event in triggers.get("events", []):
            if event not in known_events:
                errors.append(f"{skill_name} references unknown event: {event}")
        for related_key in ("requires", "conflicts"):
            for related in definition.get(related_key, []):
                if related not in skills:
                    errors.append(f"{skill_name} {related_key} unknown skill: {related}")
                if related == skill_name:
                    errors.append(f"{skill_name} cannot {related_key} itself")

    routed_paths = set(seen_paths)
    metadata_dirs = {"tests"}
    for path in (repository_root / "agent-skills").glob("*/SKILL.md"):
        if path.parent.name in metadata_dirs:
            continue
        relative = path.relative_to(repository_root).as_posix()
        if relative not in routed_paths:
            errors.append(f"unrouted skill file: {relative}")

    state: dict[str, int] = {}

    def visit(skill_name: str, chain: tuple[str, ...] = ()) -> None:
        current = state.get(skill_name, 0)
        if current == 1:
            errors.append(f"dependency cycle: {' -> '.join(chain + (skill_name,))}")
            return
        if current == 2:
            return
        state[skill_name] = 1
        for required in skills[skill_name].get("requires", []):
            if required in skills:
                visit(required, chain + (skill_name,))
        state[skill_name] = 2

    for skill_name in skills:
        visit(skill_name)

    for index, rule in enumerate(routing.get("combinations", [])):
        for included in rule.get("includes", []):
            if included not in skills:
                errors.append(f"combination {index} includes unknown skill: {included}")

    for collection_name, collection in routing.get("minimal_collections", {}).items():
        if len(collection) != len(set(collection)):
            errors.append(f"minimal collection {collection_name} contains duplicates")
        for skill_name in collection:
            if skill_name not in skills:
                errors.append(f"minimal collection {collection_name} references unknown skill: {skill_name}")

    readme = repository_root / "agent-skills" / "README.md"
    if not readme.is_file():
        errors.append("missing agent-skills/README.md")
    else:
        readme_text = readme.read_text(encoding="utf-8")
        for skill_name in skills:
            if f"`{skill_name}`" not in readme_text:
                errors.append(f"README index missing skill: {skill_name}")

    regression = repository_root / "agent-skills" / "route-regression.json"
    try:
        cases = json.loads(regression.read_text(encoding="utf-8"))
        if not isinstance(cases, list) or not cases:
            errors.append("route-regression.json must contain a non-empty list")
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid route-regression.json: {exc}")

    for asset in (repository_root / "agent-skills").glob("*/assets/*.json"):
        try:
            json.loads(asset.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON asset {asset.relative_to(repository_root).as_posix()}: {exc}")

    for script in (repository_root / "agent-skills").rglob("*.py"):
        try:
            compile(script.read_text(encoding="utf-8"), str(script), "exec")
        except (OSError, SyntaxError) as exc:
            errors.append(f"invalid Python source {script.relative_to(repository_root).as_posix()}: {exc}")

    return list(dict.fromkeys(errors))


def run_regression(routing: dict) -> tuple[int, int]:
    cases = json.loads(REGRESSION_FILE.read_text(encoding="utf-8"))
    failures = 0
    for case in cases:
        project_files = case.get("project_files", [])
        if project_files:
            with tempfile.TemporaryDirectory() as directory:
                project_root = Path(directory)
                for relative in project_files:
                    target = project_root / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_text(case.get("project_contents", {}).get(relative, "{}\n" if target.name == "package.json" else "\n"), encoding="utf-8")
                result = resolve_skills(case["query"], routing, events=case.get("events", []), project_root=project_root, files=case.get("files", []))
        else:
            result = resolve_skills(case["query"], routing, events=case.get("events", []), files=case.get("files", []))
        actual = result["files"]
        expected = case["expected"]
        if actual != expected:
            failures += 1
            print(f"FAIL {case['name']}: expected {expected}, got {actual}")
        else:
            print(f"PASS {case['name']}")
    return len(cases), failures


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve deterministic Agent Skill bundles.")
    parser.add_argument("text", nargs="*", help="Task text or keywords")
    parser.add_argument("--event", action="append", default=[], help="Runtime event; may be repeated")
    parser.add_argument("--project-root", type=Path, help="Project root used for manifest-based routing")
    parser.add_argument("--file", action="append", default=[], help="Target file path (repeatable); scopes manifest loading without reading source")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    parser.add_argument("--explain", action="store_true", help="Show why each skill matched")
    parser.add_argument("--self-test", action="store_true", help="Run routing regression cases")
    parser.add_argument("--check", action="store_true", help="Validate routing, bundles, dependencies, and index")
    args = parser.parse_args()

    routing = json.loads(ROUTING_FILE.read_text(encoding="utf-8"))
    if args.check:
        errors = validate_routing(routing)
        if errors:
            for error in errors:
                print(f"ERROR {error}")
            return 1
        print("Routing manifest and skill bundles are valid")
        return 0

    if args.self_test:
        total, failures = run_regression(routing)
        print(f"\n{total - failures}/{total} routing cases passed")
        return int(bool(failures))

    if not args.text and not args.event and not args.file and args.project_root is None:
        parser.error("provide task text, --file, --event, --project-root, --self-test, or --check")

    query = " ".join(args.text)
    result = resolve_skills(query, routing, events=args.event, project_root=args.project_root, files=args.file)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0 if result["files"] else 1

    if not result["files"]:
        print("No routing trigger matched.")
        return 1
    print("Resolved skills:")
    for skill_name, file_name in zip(result["skills"], result["files"]):
        if args.explain:
            reason = ", ".join(result["reasons"].get(skill_name, []))
            print(f"- {file_name} ({reason})")
        else:
            print(f"- {file_name}")
    if result["warnings"]:
        print("\nWarnings:")
        for warning in result["warnings"]:
            print(f"- {warning}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

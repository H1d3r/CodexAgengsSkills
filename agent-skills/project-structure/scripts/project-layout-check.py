#!/usr/bin/env python3
"""Read-only project layout auditor and path classifier."""

from __future__ import annotations

import argparse
import fnmatch
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

POLICY_FILE = Path(__file__).parent.parent / "assets" / "project-layout-policy.json"
SUPPORTED_PROFILES = {"auto", "generic", "python", "go", "rust", "js-ts", "java", "dotnet", "android", "ios", "monorepo"}


@dataclass(frozen=True)
class Finding:
    severity: str
    rule_id: str
    path: str
    expected: str
    reason: str


def load_policy(path: Path = POLICY_FILE, project_root: Path | None = None) -> dict:
    policy = json.loads(path.read_text(encoding="utf-8"))
    if project_root is None:
        return policy
    override_path = project_root / ".agent-layout.json"
    if not override_path.is_file():
        return policy
    override = json.loads(override_path.read_text(encoding="utf-8"))
    allowed_additions = {
        "root_markdown_allowlist_add": "root_markdown_allowlist",
        "ignored_directory_names_add": "ignored_directory_names",
        "runtime_directory_names_add": "runtime_directory_names",
    }
    for source, target in allowed_additions.items():
        values = override.get(source, [])
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise ValueError(f"{source} must be a list of strings")
        policy[target] = list(dict.fromkeys(policy.get(target, []) + values))
    return policy


def _read_package_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def detect_profiles(root: Path) -> list[str]:
    """Detect conservative project profiles from root-level manifests and shallow workspace facts."""
    profiles: set[str] = {"generic"}

    def exists(name: str) -> bool:
        return (root / name).exists()

    if any(exists(name) for name in ("pyproject.toml", "setup.py", "setup.cfg", "uv.lock", "requirements.txt")):
        profiles.add("python")
    if exists("go.mod") or exists("go.work"):
        profiles.add("go")
    if exists("Cargo.toml"):
        profiles.add("rust")
    if exists("package.json") or exists("tsconfig.json") or exists("jsconfig.json"):
        profiles.add("js-ts")
    if exists("pom.xml") or exists("build.gradle") or exists("build.gradle.kts"):
        profiles.add("java")
    if list(root.glob("*.sln")) or list(root.glob("*.slnx")) or list(root.glob("*.csproj")) or exists("Directory.Build.props"):
        profiles.add("dotnet")
    if exists("AndroidManifest.xml") or list(root.glob("*/src/main/AndroidManifest.xml")):
        profiles.add("android")
    if list(root.glob("*.xcodeproj")) or list(root.glob("*.xcworkspace")):
        profiles.add("ios")

    if exists("pnpm-workspace.yaml") or exists("nx.json") or exists("turbo.json") or exists("go.work"):
        profiles.add("monorepo")
    package = _read_package_json(root / "package.json") if exists("package.json") else {}
    if package.get("workspaces"):
        profiles.add("monorepo")
    cargo = root / "Cargo.toml"
    if cargo.is_file():
        try:
            if "[workspace]" in cargo.read_text(encoding="utf-8"):
                profiles.add("monorepo")
        except OSError:
            pass

    shallow_manifests = 0
    for pattern in ("*/pyproject.toml", "*/go.mod", "*/Cargo.toml", "*/package.json", "*/pom.xml", "*/*.csproj"):
        shallow_manifests += sum(1 for _ in root.glob(pattern))
    if shallow_manifests > 1:
        profiles.add("monorepo")

    order = ["generic", "monorepo", "python", "go", "rust", "js-ts", "java", "dotnet", "android", "ios"]
    return [profile for profile in order if profile in profiles]


def classify_path(relative_path: str | Path) -> tuple[str, str]:
    path = Path(relative_path)
    lower_parts = [part.lower() for part in path.parts]
    name = path.name.lower()
    suffix = path.suffix.lower()

    if name in {".env", ".env.local", ".env.production", "credentials.json", "secrets.json"}:
        return "secret", "external secret storage or an untracked local configuration"
    if suffix in {".log", ".dump", ".core", ".tmp", ".swp", ".pyc"} or name == ".ds_store":
        return "runtime-artifact", "the system temporary directory or an explicitly ignored artifact directory"
    if any(part in {"docs", "documentation"} for part in lower_parts) or suffix == ".md":
        return "documentation", "docs/<plans|design|adr|runbooks|reports|archive>/"
    if any(part in {"migrations", "migration"} for part in lower_parts):
        return "migration", "the migrations directory owned by the relevant service or data model"
    if suffix in {".proto", ".graphql", ".gql"} or "openapi" in name or any(part in {"openapi", "proto", "schema"} for part in lower_parts):
        return "api-schema", "the existing API contract directory owned by the relevant service"
    if any(part in {"e2e", "end-to-end"} for part in lower_parts):
        return "e2e-test", "the existing e2e test root"
    if any(part in {"integration", "integration-tests"} for part in lower_parts):
        return "integration-test", "the existing integration test root"
    if any(part in {"fixtures", "fixture", "testdata"} for part in lower_parts):
        return "fixture", "the nearest owning test directory"
    if any(part in {"snapshots", "__snapshots__"} for part in lower_parts) or name.endswith(".snap"):
        return "snapshot", "the test framework snapshot directory"
    if any(part in {"test", "tests", "spec", "specs", "__tests__"} for part in lower_parts) or any(marker in name for marker in ("_test.", ".test.", ".spec.")):
        return "unit-test", "the existing unit test convention or a tests/ tree mirroring source"
    if any(part in {"scripts", "script"} for part in lower_parts):
        return "script", "scripts/ or the existing automation directory"
    if any(part in {"tools", "tooling"} for part in lower_parts):
        return "tooling", "tools/ or an existing workspace tool package"
    if any(part in {"deploy", "deployment", "infra", "terraform", "k8s", "helm"} for part in lower_parts):
        return "deployment", "deploy/, infra/, or the deployment tool's required path"
    if any(part in {"assets", "static", "public", "resources"} for part in lower_parts):
        return "asset", "the owning application or package resource directory"
    if "generated" in lower_parts or name.endswith((".generated.ts", ".generated.cs", ".pb.go")):
        return "generated", "the generator-configured output directory"
    return "source", "the existing language or framework source root"


def _walk(root: Path, ignored: set[str], pruned: set[str]) -> Iterable[Path]:
    for current, directories, files in os.walk(root):
        current_path = Path(current)
        next_directories: list[str] = []
        for name in directories:
            if name in ignored:
                continue
            yield current_path / name
            if name not in pruned:
                next_directories.append(name)
        directories[:] = next_directories
        for name in files:
            yield current_path / name


def audit(root: Path, policy: dict, forced_profile: str = "auto") -> dict:
    root = root.resolve()
    profiles = detect_profiles(root) if forced_profile == "auto" else ["generic", forced_profile] if forced_profile != "generic" else ["generic"]
    findings: list[Finding] = []
    allow_markdown = set(policy.get("root_markdown_allowlist", []))

    for path in sorted(root.glob("*.md")):
        if path.name not in allow_markdown:
            findings.append(Finding(
                "error",
                "root-markdown",
                path.name,
                "docs/ or a subproject docs/ directory",
                "Root Markdown is limited to AGENTS.md and README.md unless the project policy explicitly adds an exception.",
            ))

    ignored = set(policy.get("ignored_directory_names", []))
    runtime_dirs = set(policy.get("runtime_directory_names", []))
    runtime_patterns = policy.get("runtime_file_patterns", [])
    secret_names = set(policy.get("secret_file_names", []))
    secret_templates = set(policy.get("allowed_secret_templates", []))

    for path in _walk(root, ignored, runtime_dirs):
        try:
            relative = path.relative_to(root)
        except ValueError:
            continue
        if path.is_dir() and path.name in runtime_dirs:
            severity = "error" if path.name == "__pycache__" else "warning"
            findings.append(Finding(
                severity,
                "runtime-directory",
                relative.as_posix(),
                "an ignored build/cache location outside committed source",
                f"{path.name} is a generated runtime or build directory.",
            ))
            continue
        if not path.is_file():
            continue
        if path.name in secret_names and path.name not in secret_templates:
            findings.append(Finding(
                "warning",
                "secret-file",
                relative.as_posix(),
                "external secret storage or an untracked local file",
                "The file name commonly contains real environment credentials; content was not inspected.",
            ))
        if any(fnmatch.fnmatch(path.name, pattern) for pattern in runtime_patterns):
            findings.append(Finding(
                "error",
                "runtime-file",
                relative.as_posix(),
                "the system temporary directory or an explicitly ignored artifact directory",
                "Runtime, cache, editor, or debug output must not be mixed with source files.",
            ))

    counts = {severity: sum(1 for finding in findings if finding.severity == severity) for severity in ("error", "warning", "info")}
    return {
        "profiles": profiles,
        "findings": [asdict(finding) for finding in findings],
        "summary": counts,
        "exit_code": 1 if counts["error"] else 0,
    }


def explain(path: str) -> dict:
    category, expected = classify_path(path)
    return {
        "path": Path(path).as_posix(),
        "category": category,
        "expected": expected,
        "reason": "Classification is advisory; existing project and framework conventions take precedence.",
    }


def print_human(result: dict) -> None:
    print(f"Profiles: {', '.join(result['profiles'])}")
    for finding in result["findings"]:
        print(f"{finding['severity'].upper()} {finding['rule_id']} {finding['path']}")
        print(f"  expected: {finding['expected']}")
        print(f"  reason: {finding['reason']}")
    summary = result["summary"]
    print(f"Summary: {summary['error']} error(s), {summary['warning']} warning(s), {summary['info']} info finding(s)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit project layout without modifying files.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root to inspect")
    parser.add_argument("--profile", default="auto", choices=sorted(SUPPORTED_PROFILES), help="Force a layout profile")
    parser.add_argument("--check", action="store_true", help="Run the audit and return a failing exit code for errors")
    parser.add_argument("--json", action="store_true", help="Output structured JSON")
    parser.add_argument("--explain", metavar="PATH", help="Classify one proposed relative path")
    args = parser.parse_args()

    if args.explain:
        result = explain(args.explain)
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"Path: {result['path']}")
            print(f"Category: {result['category']}")
            print(f"Expected: {result['expected']}")
            print(f"Reason: {result['reason']}")
        return 0

    if not args.root.is_dir():
        parser.error(f"root is not a directory: {args.root}")
    try:
        policy = load_policy(project_root=args.root.resolve())
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        parser.error(f"invalid .agent-layout.json: {exc}")
    result = audit(args.root, policy, args.profile)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_human(result)
    return result["exit_code"] if args.check or args.json else 0


if __name__ == "__main__":
    raise SystemExit(main())

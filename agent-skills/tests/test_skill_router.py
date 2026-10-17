from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
MODULE_PATH = ROOT / "agent-skills" / "skill-router.py"
SPEC = importlib.util.spec_from_file_location("skill_router", MODULE_PATH)
assert SPEC and SPEC.loader
skill_router = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(skill_router)


class SkillRouterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.routing = json.loads((ROOT / "agent-skills" / "skill-routing.json").read_text(encoding="utf-8"))

    def test_file_create_event_routes_project_structure(self) -> None:
        result = skill_router.resolve_skills("add helper", self.routing, events=["file-create"])
        self.assertEqual(result["skills"], ["project-structure"])
        self.assertEqual(result["reasons"]["project-structure"], ["event:file-create"])

    def test_project_fact_routes_python(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
            result = skill_router.resolve_skills("review implementation", self.routing, project_root=root)
        self.assertEqual(result["skills"], ["python"])
        self.assertIn("project-fact:python", result["reasons"]["python"])

    def test_pi_math_does_not_route_runtime(self) -> None:
        result = skill_router.resolve_skills("calculate pi to ten digits", self.routing)
        self.assertNotIn("agent-runtime-compat", result["skills"])

    def test_chinese_phrase_routes_project_structure(self) -> None:
        result = skill_router.resolve_skills("请整理文件并优化目录结构", self.routing)
        self.assertEqual(result["skills"], ["project-structure"])

    def test_order_is_keyword_invariant(self) -> None:
        first = skill_router.resolve_skills("python api testing", self.routing)["files"]
        second = skill_router.resolve_skills("testing api python", self.routing)["files"]
        self.assertEqual(first, second)

    def test_repository_manifest_is_valid(self) -> None:
        self.assertEqual(skill_router.validate_routing(self.routing, ROOT), [])

    def test_target_files_scope_manifest_loading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "package.json").write_text(
                '{"dependencies":{"react":"1","vue":"3"},"devDependencies":{"typescript":"5"}}',
                encoding="utf-8",
            )
            result = skill_router.resolve_skills("review implementation", self.routing,
                                                project_root=root, files=["src/parser.ts"])
        self.assertEqual(result["skills"], ["javascript-typescript", "typescript"])
        self.assertEqual(result["project_facts"], [])
        self.assertEqual(result["reasons"]["typescript"], ["file:src/parser.ts"])

    def test_target_files_do_not_override_explicit_task(self) -> None:
        result = skill_router.resolve_skills("review Vue and TypeScript", self.routing, files=["src/a.py"])
        self.assertIn("python", result["skills"])
        self.assertIn("typescript", result["skills"])
        self.assertIn("frontend-vue", result["skills"])

    def test_file_patterns_are_case_sensitive_and_deduplicated(self) -> None:
        result = skill_router.resolve_skills("review", self.routing, files=["src/a.ts", "src/a.ts", "src/other.TS"])
        self.assertEqual(result["target_files"], ["src/a.ts", "src/other.TS"])
        self.assertEqual(result["skills"].count("typescript"), 1)
        self.assertEqual(result["reasons"]["typescript"], ["file:src/a.ts"])

    def test_windows_target_path_normalization(self) -> None:
        result = skill_router.resolve_skills("review", self.routing, files=[r"src\App.vue"])
        self.assertEqual(result["target_files"], ["src/App.vue"])
        self.assertEqual(result["skills"], ["frontend-vue", "frontend-framework"])

    def test_shared_ownership_terms_do_not_load_rust(self) -> None:
        result = skill_router.resolve_skills("C++ ownership and lifetime", self.routing)
        self.assertEqual(result["skills"], ["cpp"])
        result = skill_router.resolve_skills("ownership in rust", self.routing)
        self.assertEqual(result["skills"], ["rust", "rust-pro"])

    def test_package_manifest_handles_invalid_shapes(self) -> None:
        for content in ("[]", "null", '{"dependencies":null}', '{"devDependencies":["vue"]}', "not JSON"):
            with self.subTest(content=content), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "package.json").write_text(content, encoding="utf-8")
                self.assertEqual(skill_router.detect_project_facts(root), ["javascript-typescript"])

    def test_project_typescript_vue_and_cpp_facts(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "tsconfig.app.json").write_text("{}", encoding="utf-8")
            (root / "package.json").write_text('{"dependencies":{"vue":"3"}}', encoding="utf-8")
            (root / "CMakeLists.txt").write_text("project(app LANGUAGES CXX)", encoding="utf-8")
            facts = skill_router.detect_project_facts(root)
        self.assertEqual(facts, ["cpp", "frontend", "javascript-typescript", "typescript", "vue"])

    def test_cmake_comment_and_c_project_do_not_load_cpp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CMakeLists.txt").write_text("# project(example CXX)\nproject(app LANGUAGES C)", encoding="utf-8")
            self.assertNotIn("cpp", skill_router.detect_project_facts(root))

    def test_ambiguous_jsx_files_do_not_assume_react(self) -> None:
        for target in ("src/render.tsx", "src/render.jsx"):
            with self.subTest(target=target):
                result = skill_router.resolve_skills("review", self.routing, files=[target])
                self.assertNotIn("frontend-react", result["skills"])
                self.assertNotIn("frontend-vue", result["skills"])

    def test_cmake_non_language_cxx_mentions_do_not_load_cpp(self) -> None:
        cases = [
            'project(app DESCRIPTION "CXX tooling" LANGUAGES C)',
            'project(CXX LANGUAGES C)',
            'project(app LANGUAGES C DESCRIPTION CXX)',
            'project(app DESCRIPTION [=[CXX tooling]=] LANGUAGES C)',
            'project(app LANGUAGES ${CXX})',
        ]
        for source in cases:
            with self.subTest(source=source), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                (root / "CMakeLists.txt").write_text(source, encoding="utf-8")
                self.assertNotIn("cpp", skill_router.detect_project_facts(root))

    def test_cmake_enable_language_routes_cpp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CMakeLists.txt").write_text("project(app LANGUAGES C)\nenable_language(CXX)", encoding="utf-8")
            self.assertIn("cpp", skill_router.detect_project_facts(root))

    def test_cmake_bracket_comments_do_not_load_cpp(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CMakeLists.txt").write_text("#[=[\nproject(example CXX)\n]=]\nproject(app LANGUAGES C)", encoding="utf-8")
            self.assertNotIn("cpp", skill_router.detect_project_facts(root))

    def test_visual_and_dispatch_events_are_opt_in(self) -> None:
        result = skill_router.resolve_skills("review task", self.routing)
        self.assertNotIn("frontend-design", result["skills"])
        self.assertNotIn("subagent-workflow", result["skills"])
        self.assertEqual(skill_router.resolve_skills("", self.routing, events=["ui-design"])["skills"], ["frontend-design"])
        self.assertEqual(skill_router.resolve_skills("", self.routing, events=["task-dispatch"])["skills"], ["subagent-workflow"])

    def test_cli_file_only_returns_scoped_json(self) -> None:
        result = subprocess.run([sys.executable, "-B", str(MODULE_PATH), "--file", "src/App.vue", "--json"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["skills"], ["frontend-vue", "frontend-framework"])
        self.assertEqual(payload["target_files"], ["src/App.vue"])

    def test_cli_repeated_targets_deduplicate_shared_skills(self) -> None:
        result = subprocess.run([sys.executable, "-B", str(MODULE_PATH), "--file", "src/a.ts",
                                 "--file", "src/b.ts", "--file", "src/App.vue", "--json"],
                                capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["skills"], ["javascript-typescript", "typescript", "frontend-vue", "frontend-framework"])
        self.assertEqual(len(payload["reasons"]["typescript"]), 2)

    def test_validation_detects_dependency_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skills_root = root / "agent-skills"
            for name in ("alpha", "beta"):
                target = skills_root / name
                target.mkdir(parents=True)
                (target / "SKILL.md").write_text(
                    f"---\nname: {name}\ndescription: Test {name}.\n---\n\n# {name}\n",
                    encoding="utf-8",
                )
            (skills_root / "README.md").write_text("`alpha` `beta`\n", encoding="utf-8")
            routing = {
                "schema": "agent-skill-routing-v3",
                "events": [],
                "skills": {
                    "alpha": {
                        "path": "agent-skills/alpha/SKILL.md",
                        "level": "P1",
                        "priority": 1,
                        "triggers": {},
                        "requires": ["beta"],
                        "conflicts": [],
                        "compatibility": ["generic"],
                    },
                    "beta": {
                        "path": "agent-skills/beta/SKILL.md",
                        "level": "P1",
                        "priority": 2,
                        "triggers": {},
                        "requires": ["alpha"],
                        "conflicts": [],
                        "compatibility": ["generic"],
                    },
                },
            }
            errors = skill_router.validate_routing(routing, root)
        self.assertTrue(any(error.startswith("dependency cycle:") for error in errors))

    def test_validation_detects_missing_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "agent-skills" / "broken"
            target.mkdir(parents=True)
            (target / "SKILL.md").write_text("# Broken\n", encoding="utf-8")
            (root / "agent-skills" / "README.md").write_text("`broken`\n", encoding="utf-8")
            routing = {
                "schema": "agent-skill-routing-v3",
                "events": [],
                "skills": {
                    "broken": {
                        "path": "agent-skills/broken/SKILL.md",
                        "level": "P1",
                        "priority": 1,
                        "triggers": {},
                        "requires": [],
                        "conflicts": [],
                        "compatibility": ["generic"],
                    }
                },
            }
            errors = skill_router.validate_routing(routing, root)
        self.assertTrue(any("missing YAML frontmatter" in error for error in errors))


if __name__ == "__main__":
    unittest.main()

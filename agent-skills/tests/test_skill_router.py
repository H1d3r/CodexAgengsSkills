from __future__ import annotations

import importlib.util
import json
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

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).parents[2]
MODULE_PATH = ROOT / "agent-skills" / "project-structure" / "scripts" / "project-layout-check.py"
SPEC = importlib.util.spec_from_file_location("project_layout_check", MODULE_PATH)
assert SPEC and SPEC.loader
layout = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = layout
SPEC.loader.exec_module(layout)


class ProjectLayoutCheckTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy = layout.load_policy()

    def test_allowed_root_markdown_and_docs_pass(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")
            (root / "docs" / "plans").mkdir(parents=True)
            (root / "docs" / "plans" / "change.md").write_text("# Plan\n", encoding="utf-8")
            result = layout.audit(root, self.policy)
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["findings"], [])

    def test_stray_root_markdown_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "progress.md").write_text("progress\n", encoding="utf-8")
            result = layout.audit(root, self.policy)
        self.assertEqual(result["exit_code"], 1)
        self.assertEqual(result["findings"][0]["rule_id"], "root-markdown")

    def test_runtime_file_fails(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "server.log").write_text("log\n", encoding="utf-8")
            result = layout.audit(root, self.policy)
        self.assertEqual(result["exit_code"], 1)
        self.assertTrue(any(item["rule_id"] == "runtime-file" for item in result["findings"]))

    def test_secret_file_warns_without_reading_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".env").write_text("DO_NOT_READ=this-value\n", encoding="utf-8")
            result = layout.audit(root, self.policy)
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(result["summary"]["warning"], 1)

    def test_profile_detection(self) -> None:
        cases = {
            "python": "pyproject.toml",
            "go": "go.mod",
            "rust": "Cargo.toml",
            "js-ts": "package.json",
            "java": "pom.xml",
            "dotnet": "Demo.sln",
        }
        for expected, manifest in cases.items():
            with self.subTest(expected=expected), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                content = "{}\n" if manifest == "package.json" else "\n"
                (root / manifest).write_text(content, encoding="utf-8")
                self.assertIn(expected, layout.detect_profiles(root))

    def test_android_and_ios_detection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = root / "app" / "src" / "main" / "AndroidManifest.xml"
            manifest.parent.mkdir(parents=True)
            manifest.write_text("<manifest />\n", encoding="utf-8")
            (root / "Demo.xcodeproj").mkdir()
            profiles = layout.detect_profiles(root)
        self.assertIn("android", profiles)
        self.assertIn("ios", profiles)

    def test_monorepo_detection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "pnpm-workspace.yaml").write_text("packages: []\n", encoding="utf-8")
            self.assertIn("monorepo", layout.detect_profiles(root))

    def test_existing_custom_source_root_is_not_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "custom-code" / "module.py"
            source.parent.mkdir()
            source.write_text("VALUE = 1\n", encoding="utf-8")
            before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
            result = layout.audit(root, self.policy)
            after = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
        self.assertEqual(result["exit_code"], 0)
        self.assertEqual(before, after)


    def test_project_policy_can_add_root_markdown_exception(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "CHANGELOG.md").write_text("# Changes\n", encoding="utf-8")
            (root / ".agent-layout.json").write_text(
                '{"root_markdown_allowlist_add": ["CHANGELOG.md"]}\n',
                encoding="utf-8",
            )
            policy = layout.load_policy(project_root=root)
            result = layout.audit(root, policy)
        self.assertEqual(result["exit_code"], 0)

    def test_explain_classifies_migration(self) -> None:
        result = layout.explain("services/orders/migrations/001_init.sql")
        self.assertEqual(result["category"], "migration")


if __name__ == "__main__":
    unittest.main()

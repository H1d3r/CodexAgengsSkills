from __future__ import annotations

import copy
import importlib.util
import json
import unittest
from pathlib import Path

BUNDLE = Path(__file__).parents[1] / "frontend-design"
SPEC = importlib.util.spec_from_file_location("design_token_validator", BUNDLE / "scripts/validate-tokens.py")
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


class FrontendDesignTokenTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tokens = json.loads((BUNDLE / "assets/design-tokens.json").read_text(encoding="utf-8"))
        cls.css = (BUNDLE / "assets/design-tokens.css").read_text(encoding="utf-8")

    def test_shipped_token_contract_and_accessibility_preferences(self) -> None:
        cases, ratios = validator.validate(self.tokens, self.css)
        self.assertEqual(cases, 48)
        self.assertGreaterEqual(min(ratios["text"]), 4.5)
        self.assertGreaterEqual(min(ratios["non-text"]), 3)
        self.assertEqual(self.tokens["preferences"]["reduced-motion"],
                         {"duration-fast": "0ms", "duration-normal": "0ms", "motion-distance": "0px"})
        colors = self.tokens["preferences"]["forced-colors"]
        for name, value in colors.items():
            if name.startswith("color-") and name != "color-scheme":
                self.assertIn(value, {"Canvas", "CanvasText", "LinkText", "Highlight"})
        self.assertEqual(colors["shadow-overlay"], "none")

    def test_css_drift_fails_even_when_json_is_valid(self) -> None:
        css = self.css.replace("--fd-space-1: 0.25rem;", "--fd-space-1: 9rem;", 1)
        self.assertNotEqual(css, self.css)
        with self.assertRaisesRegex(ValueError, "differ from JSON contract"):
            validator.validate(self.tokens, css)

    def test_synchronized_low_contrast_seed_fails(self) -> None:
        tokens = copy.deepcopy(self.tokens)
        tokens["themes"]["light"]["color-muted"] = "#ffffff"
        css = self.css.replace("--fd-color-muted: #526071;", "--fd-color-muted: #ffffff;", 1)
        with self.assertRaisesRegex(ValueError, "Low contrast"):
            validator.validate(tokens, css)


if __name__ == "__main__":
    unittest.main()

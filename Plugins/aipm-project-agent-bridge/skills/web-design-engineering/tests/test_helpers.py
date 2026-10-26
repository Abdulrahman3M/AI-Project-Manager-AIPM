from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


class HelperTests(unittest.TestCase):
    def test_design_brief_validator_accepts_complete_brief(self) -> None:
        validator = load("validate_design_brief")
        brief = {"thesis": "Specific", "audience": "People", "primary_job": "Act", "hierarchy": "Action first", "tokens": {"color": {}, "type": {}, "space": {}}, "verification": {"viewports": [], "states": []}}
        self.assertEqual(validator.validate(brief), [])

    def test_token_builder_flattens_safe_groups(self) -> None:
        builder = load("build_token_css")
        self.assertEqual(builder.flatten({"color": {"canvas": "#fff"}}), [("color-canvas", "#fff")])
        with self.assertRaises(ValueError):
            builder.flatten({"bad name": "#fff"})

    def test_token_template_is_valid_json(self) -> None:
        data = json.loads((ROOT / "templates" / "Design-Tokens.json").read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], "1.0")
        self.assertIn("colors", data)


if __name__ == "__main__":
    unittest.main()

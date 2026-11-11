"""Protected capability hashes must survive Git line-ending conversion."""

import hashlib
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class CapabilityGitBytesTests(unittest.TestCase):
    def test_skill_and_bridge_bytes_are_not_normalized(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "Shared-Project-State-Manager/Test-Workspace") as temporary:
            repo = Path(temporary)
            (repo / ".gitattributes").write_bytes((ROOT / ".gitattributes").read_bytes())
            samples = {
                "01-Skills-General/sample/SKILL.md": b"first\r\nsecond\n",
                "Plugins/aipm-project-agent-bridge/skills/sample/SKILL.md": b"first\r\nsecond\n",
                "02-Prompt-General/sample.md": b"first\r\nsecond\n",
                "LICENSE": b"first\r\nsecond\n",
                "NOTICE": b"first\r\nsecond\n",
            }
            registry = json.loads((ROOT / "Capability-Library/Registry.json").read_text(encoding="utf-8"))
            for slug, relative in (("audio-timing-author", "SKILL.md"),
                                   ("screenshot-to-code", "SKILL.md"),
                                   ("create-strict-implementation-handoff", "tests/fixture-master.md")):
                skill = next(item for item in registry["skills"] if item["slug"] == slug)
                name = skill["path"] + "/" + relative
                data = (ROOT / name).read_bytes()
                self.assertEqual(hashlib.sha256(data).hexdigest(), skill["files"][relative])
                samples[name] = data
            for name, data in samples.items():
                path = repo / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)
            subprocess.run(["git", "init", "--quiet", str(repo)], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(repo), "-c", "core.autocrlf=true", "add", "."], check=True, capture_output=True)
            for name, data in samples.items():
                staged = subprocess.run(["git", "-C", str(repo), "show", ":" + name], check=True, capture_output=True).stdout
                self.assertEqual(staged, data, name)
            checkout = repo / "checkout"
            checkout.mkdir()
            subprocess.run(["git", "-C", str(repo), "-c", "core.autocrlf=true", "checkout-index",
                            "--all", "--prefix=" + str(checkout) + os.sep], check=True, capture_output=True)
            for name, data in samples.items():
                self.assertEqual((checkout / name).read_bytes(), data, name)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
from test_support import CORE_ROOT
sys.path.insert(0, str(CORE_ROOT))

from aipm_core.release import ReleaseError, build_release, verify_release  # noqa: E402


class ReleasePackagingTests(unittest.TestCase):
    def setUp(self) -> None:
        workspace = ROOT / ".test-workspace"
        workspace.mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix="p10-", dir=workspace)
        self.root = Path(self.temp.name) / "AIPM"
        self._write_fixture()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_fixture(self) -> None:
        for relative, text in {
            "VERSION": "1.0.2\n",
            "CHANGELOG.md": "# Change Log\n\n## [1.0.2] — Test Release\n",
            "LICENSE": "Apache License 2.0\n",
            "NOTICE": "Copyright 2026 Abdulrahman Elbatrah\n",
            "README.md": "# AIPM\n",
            "AGENTS.md": "# Rules\n",
            "Core-Engine/aipm.py": "print('aipm')\n",
            "TUI/AI-Project-Manager/VERSION": "1.0.2\n",
            "TUI/AI-Project-Manager/CHANGELOG.md": "# TUI\n\n## [1.0.2] — Test Release\n",
            "TUI/AI-Project-Manager/Start-AIPM.ps1": "Write-Output 'AIPM'\n",
            "Plugins/aipm-project-agent-bridge/VERSION": "1.0.0\n",
            "Plugins/aipm-project-agent-bridge/CHANGELOG.md": "# Bridge\n\n## [1.0.0] — Initial\n",
            "Plugins/README.md": "# Plugins\n",
            "Plugins/Build-System/build_plugins.py": "# Builder source\n",
            "Plugins/Adapters/Host-Adapter-Contract.md": "# Adapter Contract\n",
            "Plugins/Dist/example-plugin.zip": "generated distribution output\n",
            "docs/project/Project-Rules.md": "# Rules\n",
            "docs/project/Architecture/Plugin-Distribution-Architecture.md": "# Current Architecture\n",
            "docs/project/Build-History-Archive.zip": "internal history archive\n",
            "docs/project/Provenance/Source-Revision.json": "{}\n",
            "Templates/Shared-Project-State-Manager-Example/README.md": "# Example template\n",
            ".test-workspace/trace.txt": "excluded\n",
            "Core-Engine/__pycache__/generated.pyc": "temporary cache containing fixture path\n",
        }.items():
            path = self.root / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def test_build_is_reproducible_and_verifiable(self) -> None:
        first = build_release(self.root, self.root / "Releases-A")
        second = build_release(self.root, self.root / "Releases-B")
        self.assertEqual(first["sha256"], second["sha256"])
        self.assertEqual(first["archive"].read_bytes(), second["archive"].read_bytes())
        verified = verify_release(self.root, first["archive"], first["checksum"])
        self.assertEqual(verified["status"], "PASS")
        with zipfile.ZipFile(first["archive"]) as archive:
            names = archive.namelist()
            self.assertIn("AI-Project-Manager-v1.0.2/Release-Manifest.json", names)
            self.assertIn("AI-Project-Manager-v1.0.2/docs/project/Architecture/Plugin-Distribution-Architecture.md", names)
            self.assertIn("AI-Project-Manager-v1.0.2/Templates/Shared-Project-State-Manager-Example/README.md", names)
            self.assertIn("AI-Project-Manager-v1.0.2/Plugins/README.md", names)
            self.assertIn("AI-Project-Manager-v1.0.2/Plugins/Build-System/build_plugins.py", names)
            self.assertIn("AI-Project-Manager-v1.0.2/Plugins/Adapters/Host-Adapter-Contract.md", names)
            self.assertNotIn("AI-Project-Manager-v1.0.2/Plugins/Dist/example-plugin.zip", names)
            self.assertNotIn("AI-Project-Manager-v1.0.2/docs/project/Build-History-Archive.zip", names)
            self.assertNotIn("AI-Project-Manager-v1.0.2/.test-workspace/trace.txt", names)
            self.assertNotIn("AI-Project-Manager-v1.0.2/Core-Engine/__pycache__/generated.pyc", names)
            manifest = json.loads(archive.read("AI-Project-Manager-v1.0.2/Release-Manifest.json"))
        self.assertEqual(manifest["version"], "1.0.2")

    def test_rejects_sensitive_content_and_actual_checkout_path(self) -> None:
        secret = self.root / "Core-Engine" / "credentials.json"
        secret.write_text('{"token":"not-a-real-secret"}\n', encoding="utf-8")
        with self.assertRaisesRegex(ReleaseError, "Sensitive-looking"):
            build_release(self.root, self.root / "Releases")
        secret.unlink()
        readme = self.root / "README.md"
        readme.write_text(f"# AIPM\n{self.root}\n", encoding="utf-8")
        with self.assertRaisesRegex(ReleaseError, "local checkout path"):
            build_release(self.root, self.root / "Releases")

    def test_verification_rejects_tampered_payload(self) -> None:
        built = build_release(self.root, self.root / "Releases")
        tampered = self.root / "tampered.zip"
        with zipfile.ZipFile(built["archive"]) as source, zipfile.ZipFile(tampered, "w") as destination:
            for item in source.infolist():
                data = source.read(item.filename)
                if item.filename.endswith("README.md"):
                    data += b"tampered\n"
                destination.writestr(item, data)
        shutil.copy2(built["checksum"], tampered.with_suffix(".zip.sha256"))
        with self.assertRaisesRegex(ReleaseError, "checksum|hash"):
            verify_release(self.root, tampered, tampered.with_suffix(".zip.sha256"))

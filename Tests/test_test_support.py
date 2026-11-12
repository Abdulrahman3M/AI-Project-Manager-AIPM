from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from test_support import _ensure_test_workspace


class TestSupportWorkspaceTests(unittest.TestCase):
    def test_workspace_creation_includes_missing_parent_directories(self) -> None:
        workspace_root = Path(__file__).resolve().parents[1] / "Shared-Project-State-Manager" / "Test-Workspace"
        with tempfile.TemporaryDirectory(dir=workspace_root) as temporary:
            workspace = Path(temporary) / "Missing-Parent" / "Test-Workspace"

            _ensure_test_workspace(workspace)

            self.assertTrue(workspace.is_dir())
            self.assertEqual(list(workspace.iterdir()), [])


if __name__ == "__main__":
    unittest.main()

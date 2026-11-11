"""Cross-policy record scenarios; these do not simulate a real host hook."""

import importlib.util
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GoldenTriangleScenarioTests(unittest.TestCase):
    def test_lifecycle_revision_and_failed_required_test(self):
        manager = load("triangle_manager_scenario", "01-Skills-General/project-manager/scripts/bootstrap.py")
        scope = load("triangle_scope_scenario", "01-Skills-General/task-scope-contract/scripts/scope_check.py")
        resource = load("triangle_resource_scenario", "01-Skills-General/resource-optimization/scripts/resource_policy.py")
        workspace = ROOT / "Shared-Project-State-Manager/Test-Workspace"
        with tempfile.TemporaryDirectory(dir=workspace) as temporary:
            project = Path(temporary)
            before = list(project.iterdir())
            for event in ("NEW", "ACTIVE", "RESUME", "REVISE", "REOPEN", "FIX", "RECHECK"):
                changed = event in ("REVISE", "REOPEN", "FIX")
                result = manager.bootstrap(event, "same-task", "v1", "v2" if changed else "v1")
                self.assertTrue(manager.valid_entry(result["sequence"]))
                self.assertEqual(result["scope_changed"], changed)
                self.assertEqual(result["task_key"], "same-task")
            self.assertEqual(before, list(project.iterdir()))
        budget = {"revision": "v1", "required_checks": ["unit", "regression"], "observed_calls": 2}
        revised = resource.revise_budget(budget, {"revision": "v2", "target_calls": 0})
        self.assertEqual(revised["required_checks"], ["unit", "regression"])
        self.assertTrue(resource.required_checks_continue(budget_exhausted=True))
        records = [{"id": "unit", "status": "PASS", "supported": True, "evidence": "unit output"}]
        self.assertEqual(scope.quality_gate(records, revised["required_checks"]), "UNVERIFIED")
        records.append({"id": "regression", "status": "FAIL", "supported": True, "evidence": "failure output"})
        self.assertEqual(scope.quality_gate(records, revised["required_checks"]), "FAIL")
        self.assertEqual(resource.delegation_decision("HUGE", False, {}), "SERIAL")

    def test_measured_fixture_reuses_policy_text_without_skipping_checks(self):
        manager = load("triangle_measure_manager", "01-Skills-General/project-manager/scripts/bootstrap.py")
        scope = load("triangle_measure_scope", "01-Skills-General/task-scope-contract/scripts/scope_check.py")
        paths = [ROOT / "01-Skills-General" / slug / "SKILL.md" for slug in
                 ("project-manager", "task-scope-contract", "resource-optimization")]
        events = ("NEW", "ACTIVE", "RESUME", "REVISE", "REOPEN", "FIX", "RECHECK")

        def exercise(reload_each_event):
            reads = size = 0
            started = time.perf_counter_ns()
            for index, event in enumerate(events):
                if reload_each_event or index == 0:
                    for path in paths:
                        data = path.read_bytes()
                        reads += 1
                        size += len(data)
                result = manager.bootstrap(event, "fixture", "v1", "v1")
                if not manager.valid_entry(result["sequence"]):
                    return reads, size, time.perf_counter_ns() - started, "FAIL"
                actual = scope.read_decision("verification", "v1", "v1")
                if actual != "REDUNDANT":
                    return reads, size, time.perf_counter_ns() - started, "FAIL"
            return reads, size, time.perf_counter_ns() - started, "PASS"

        baseline, reused = exercise(True), exercise(False)
        self.assertEqual((baseline[3], reused[3]), ("PASS", "PASS"))
        self.assertEqual((baseline[0], reused[0]), (21, 3))
        self.assertGreater(baseline[1], reused[1])
        print(f"Synthetic fixture (not provider quota): reads {baseline[0]}/{reused[0]}, "
              f"bytes {baseline[1]}/{reused[1]}, elapsed_ns {baseline[2]}/{reused[2]}")


if __name__ == "__main__":
    unittest.main()

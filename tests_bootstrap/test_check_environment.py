import io
import unittest

from scripts.check_environment import Probe, run_check


class CheckEnvironmentTests(unittest.TestCase):
    def test_missing_is_reported_separately_and_fails(self):
        report = io.StringIO()
        code = run_check({"pytest": Probe("missing", "pytest: not installed")}, report)
        self.assertEqual(code, 1)
        self.assertIn("MISSING:\n  - pytest: not installed", report.getvalue())
        self.assertIn("INCOMPATIBLE:\n", report.getvalue())
        self.assertIn("AVAILABLE:\n", report.getvalue())

    def test_incompatible_is_reported_separately_and_fails(self):
        report = io.StringIO()
        code = run_check({"ruff": Probe("incompatible", "ruff: 0.1, need 0.9.10")}, report)
        self.assertEqual(code, 1)
        self.assertIn("INCOMPATIBLE:\n  - ruff: 0.1, need 0.9.10", report.getvalue())
        self.assertNotIn("MISSING:\n  -", report.getvalue())

    def test_all_available_succeeds(self):
        report = io.StringIO()
        code = run_check({"python": Probe("available", "python: 3.13.5")}, report)
        self.assertEqual(code, 0)
        self.assertIn("AVAILABLE:\n  - python: 3.13.5", report.getvalue())

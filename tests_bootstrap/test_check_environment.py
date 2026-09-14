import io
import subprocess
import sys
import unittest
from unittest.mock import patch

from scripts.check_environment import Probe, python_module_probe, run_check


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

    @patch("scripts.check_environment.shutil.which")
    @patch("scripts.check_environment.subprocess.run")
    def test_tool_version_uses_selected_interpreter_not_ambient_path(
        self, run, which
    ):
        which.return_value = "/unrelated-host/bin/pytest"
        run.return_value = subprocess.CompletedProcess(
            args=[], returncode=0, stdout="pytest 8.3.5\n", stderr=""
        )

        probe = python_module_probe("pytest", "8.3.5")

        self.assertEqual(probe.state, "available")
        run.assert_called_once_with(
            [sys.executable, "-m", "pytest", "--version"],
            check=False,
            text=True,
            capture_output=True,
            timeout=5,
        )
        which.assert_not_called()

import io
import os
import subprocess
import sys
import unittest
from unittest.mock import patch

from scripts.check_environment import CANONICAL_PYTHON, Probe, main, python_module_probe, run_check


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

    @patch("scripts.check_environment.run_check", return_value=0)
    @patch("scripts.check_environment.os.access", return_value=False)
    @patch("scripts.check_environment.os.path.isfile", return_value=False)
    def test_missing_canonical_python_falls_back_with_report(self, isfile, access, run):
        self.assertEqual(main([]), 0)
        selection = run.call_args.kwargs["selection"]
        self.assertEqual(selection.state, "available")
        self.assertIn(CANONICAL_PYTHON, selection.detail)
        self.assertIn(sys.executable, selection.detail)

    @patch("scripts.check_environment.os.access", return_value=True)
    @patch("scripts.check_environment.os.path.isfile", return_value=True)
    def test_existing_selected_python_reexecs(self, isfile, access):
        selected = "/tmp/project-python"
        with patch("scripts.check_environment.os.execv", side_effect=SystemExit) as reexec:
            with self.assertRaises(SystemExit):
                main(["--python", selected])
        reexec.assert_called_once_with(
            selected, [selected, os.path.abspath("scripts/check_environment.py"), "--python", selected]
        )

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

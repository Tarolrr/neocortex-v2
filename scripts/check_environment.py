"""Read-only prerequisite report for the selected Python environment."""

from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TextIO

PYTHON_VERSION = (3, 13)
GIT_MINIMUM = (2, 40)
TOOLS = {"pytest": "8.3.5", "ruff": "0.9.10"}
IMPORTS = {"pytest": "pytest", "ruff": "ruff"}
CANONICAL_PYTHON = "/opt/neocortex-v2-runner/.venv/bin/python"


@dataclass(frozen=True)
class Probe:
    state: str  # available, missing, incompatible
    detail: str


def version_tuple(value: str) -> tuple[int, ...] | None:
    match = re.search(r"\d+(?:\.\d+)+", value)
    return tuple(int(part) for part in match.group().split(".")) if match else None


def command_probe(command: str, expected: tuple[int, ...] | str) -> Probe:
    path = shutil.which(command)
    if path is None:
        return Probe("missing", f"{command}: executable is not on PATH")
    try:
        completed = subprocess.run(
            [command, "--version"], check=False, text=True, capture_output=True, timeout=5
        )
    except (OSError, subprocess.SubprocessError) as error:
        return Probe("missing", f"{command}: cannot run ({error})")
    output = (completed.stdout + completed.stderr).strip()
    actual = version_tuple(output)
    if completed.returncode or actual is None:
        return Probe("incompatible", f"{command}: unusable version output {output!r}")
    wanted = expected if isinstance(expected, tuple) else version_tuple(expected)
    assert wanted is not None
    compatible = actual >= wanted if isinstance(expected, tuple) else actual == wanted
    if not compatible:
        relation = f">={'.'.join(map(str, wanted))}" if isinstance(expected, tuple) else expected
        return Probe("incompatible", f"{command}: {'.'.join(map(str, actual))}, need {relation}")
    return Probe("available", f"{command}: {'.'.join(map(str, actual))} ({path})")


def python_module_probe(module: str, expected: str) -> Probe:
    """Check a tool through the interpreter selected to run this script.

    Console-script lookup would inspect the caller's ambient PATH, which can
    belong to a different virtual environment than ``sys.executable``.
    """
    command = [sys.executable, "-m", module, "--version"]
    try:
        completed = subprocess.run(
            command, check=False, text=True, capture_output=True, timeout=5
        )
    except (OSError, subprocess.SubprocessError) as error:
        return Probe("missing", f"{module}: cannot run in {sys.executable} ({error})")
    output = (completed.stdout + completed.stderr).strip()
    actual = version_tuple(output)
    if completed.returncode or actual is None:
        return Probe("missing", f"{module}: not runnable in {sys.executable}: {output!r}")
    wanted = version_tuple(expected)
    assert wanted is not None
    if actual != wanted:
        return Probe("incompatible", f"{module}: {'.'.join(map(str, actual))}, need {expected}")
    return Probe("available", f"{module}: {'.'.join(map(str, actual))} ({sys.executable} -m {module})")


def python_probe() -> Probe:
    actual = sys.version_info[:2]
    if actual != PYTHON_VERSION:
        return Probe("incompatible", f"python: {actual[0]}.{actual[1]}, need {PYTHON_VERSION[0]}.{PYTHON_VERSION[1]}.x")
    return Probe("available", f"python: {sys.version.split()[0]} ({sys.executable})")


def import_probe(module: str) -> Probe:
    if importlib.util.find_spec(module) is None:
        return Probe("missing", f"import {module}: not installed in {sys.executable}")
    return Probe("available", f"import {module}: available")


def collect(
    probes: Mapping[str, Probe] | None = None, selection: Probe | None = None
) -> dict[str, Probe]:
    if probes is not None:
        return dict(probes)
    result = {"python": python_probe(), "git": command_probe("git", GIT_MINIMUM)}
    if selection is not None:
        result["interpreter-selection"] = selection
    for tool, version in TOOLS.items():
        result[tool] = python_module_probe(tool, version)
    for tool, module in IMPORTS.items():
        result[f"import:{module}"] = import_probe(module)
    return result


def run_check(
    probes: Mapping[str, Probe] | None = None,
    stream: TextIO | None = None,
    selection: Probe | None = None,
) -> int:
    stream = stream or sys.stdout
    grouped = {state: [] for state in ("missing", "incompatible", "available")}
    for probe in collect(probes, selection).values():
        grouped.setdefault(probe.state, []).append(probe.detail)
    for state in ("missing", "incompatible", "available"):
        print(f"{state.upper()}:", file=stream)
        for detail in grouped[state]:
            print(f"  - {detail}", file=stream)
    return 1 if grouped["missing"] or grouped["incompatible"] else 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--python",
        default=CANONICAL_PYTHON,
        help=(
            "interpreter to inspect (default: %(default)s); if it exists, "
            "the script re-execs itself with it"
        ),
    )
    args = parser.parse_args(argv)
    selected = os.path.abspath(args.python)
    if os.path.isfile(selected) and os.access(selected, os.X_OK):
        # A venv's ``python`` is often a symlink to the host binary, so
        # samefile() would incorrectly say that a host invocation is already
        # inside the venv.  sys.executable preserves the invocation path.
        same_interpreter = os.path.abspath(sys.executable) == selected
        if not same_interpreter:
            os.execv(selected, [selected, os.path.abspath(__file__), "--python", selected])
        selection = Probe("available", f"interpreter selection: {selected}")
    else:
        selection = Probe(
            "available",
            f"interpreter selection: {selected} is unavailable; using {sys.executable}",
        )
    return run_check(selection=selection)


if __name__ == "__main__":
    raise SystemExit(main())

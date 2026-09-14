from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def run_cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "neocortex_v2", *arguments],
        text=True,
        capture_output=True,
        check=False,
    )


def test_config_check_accepts_complete_local_configuration(tmp_path: Path) -> None:
    workdir = tmp_path / "work"
    state_dir = tmp_path / "state"
    workdir.mkdir()
    state_dir.mkdir()
    result = run_cli(
        "config-check", "--namespace", "isolated-smoke", "--base-url", "http://127.0.0.1:4096",
        "--workdir", str(workdir), "--state-dir", str(state_dir), "--provider", "example-provider",
        "--model", "example-model",
    )
    assert result.returncode == 0
    assert "offline" in result.stdout


def test_config_check_rejects_incomplete_configuration_without_secret_echo() -> None:
    secret = "dont-print-this-token"
    result = run_cli("config-check", "--namespace", "isolated", "--base-url", secret)
    assert result.returncode != 0
    assert "--workdir" in result.stderr
    assert secret not in result.stdout + result.stderr


def test_help_and_config_check_do_not_import_network_client(monkeypatch, tmp_path: Path) -> None:
    from neocortex_v2.__main__ import main

    calls: list[object] = []

    def forbidden(*args: object, **kwargs: object) -> object:
        calls.append((args, kwargs))
        raise AssertionError("network call")

    monkeypatch.setattr("socket.create_connection", forbidden)
    with pytest.raises(SystemExit) as help_exit:
        main(["--help"])
    assert help_exit.value.code == 0
    assert main(["config-check", "--namespace", "test", "--base-url", "https://localhost:4096", "--workdir", str(tmp_path), "--state-dir", str(tmp_path), "--provider", "provider", "--model", "model"]) == 0
    assert calls == []

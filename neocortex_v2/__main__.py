"""Minimal offline CLI; it intentionally cannot dispatch work."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from .config import CoordinatorConfig, validate_config


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Offline checks for the neocortex-v2 coordinator.")
    commands = parser.add_subparsers(dest="command")
    check = commands.add_parser("config-check", help="validate local configuration without network calls")
    check.add_argument("--namespace", required=True, help="OpenCode namespace or store identity")
    check.add_argument("--base-url", required=True, help="OpenCode base URL")
    check.add_argument("--workdir", required=True, type=Path, help="existing working directory")
    check.add_argument("--state-dir", required=True, type=Path, help="existing state directory")
    check.add_argument("--provider", required=True, help="explicit provider identifier")
    check.add_argument("--model", required=True, help="explicit model identifier")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    if arguments.command != "config-check":
        parser.print_help()
        return 0
    config = CoordinatorConfig(
        namespace=arguments.namespace,
        base_url=arguments.base_url,
        workdir=arguments.workdir,
        state_dir=arguments.state_dir,
        provider=arguments.provider,
        model=arguments.model,
    )
    errors = validate_config(config)
    if errors:
        for error in errors:
            print(f"configuration error: {error}")
        return 2
    print("configuration is valid (offline; no server or model call was made)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

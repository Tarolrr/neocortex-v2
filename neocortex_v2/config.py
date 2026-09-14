"""Configuration validation that deliberately performs no network calls."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


@dataclass(frozen=True)
class CoordinatorConfig:
    namespace: str
    base_url: str
    workdir: Path
    state_dir: Path
    provider: str
    model: str


def validate_config(config: CoordinatorConfig) -> list[str]:
    """Return safe diagnostics without connecting to OpenCode or a provider."""
    errors: list[str] = []
    if not config.namespace.strip():
        errors.append("namespace is required")
    parsed_url = urlparse(config.base_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        errors.append("base URL must be an absolute http(s) URL")
    if not config.workdir.is_dir():
        errors.append("working directory must exist and be a directory")
    if not config.state_dir.is_dir():
        errors.append("state directory must exist and be a directory")
    if not config.provider.strip():
        errors.append("provider is required")
    if not config.model.strip():
        errors.append("model is required")
    return errors

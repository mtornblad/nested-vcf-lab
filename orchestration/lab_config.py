"""Shared configuration loading for umbrella component adapters."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Mapping


LAB_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = LAB_ROOT / "configuration" / "lab.local.json"
CONFIG_SCHEMA = "nested-vcf-lab.config/v1"


class LabConfigError(ValueError):
    """Raised when the umbrella configuration is missing or invalid."""


def mapping(config: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = config.get(key)
    if not isinstance(value, Mapping):
        raise LabConfigError(f"{key} must be a JSON object")
    return value


def resolve_from_root(value: object) -> Path:
    path = Path(str(value)).expanduser()
    return path.resolve() if path.is_absolute() else (LAB_ROOT / path).resolve()


def load_config(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise LabConfigError(
            f"Configuration does not exist: {path}. Copy configuration/lab.example.json first."
        ) from error
    except (OSError, json.JSONDecodeError) as error:
        raise LabConfigError(f"Unable to read {path}: {error}") from error
    if not isinstance(value, dict) or value.get("schema") != CONFIG_SCHEMA:
        raise LabConfigError(f"schema must be {CONFIG_SCHEMA}")
    mapping(value, "general")
    mapping(value, "vyos")
    mapping(value, "esxi")
    return value


def general_environment(config: Mapping[str, Any]) -> dict[str, object]:
    """Translate settings inherited by every vCenter-aware component."""

    general = mapping(config, "general")
    return {
        "GOVC_URL": general.get("vcenter_url"),
        "GOVC_USERNAME": general.get("vcenter_username"),
        "GOVC_PASSWORD": general.get("vcenter_password"),
        "GOVC_INSECURE": general.get("vcenter_insecure", False),
    }


def apply_environment(values: Mapping[str, object]) -> dict[str, str]:
    """Apply umbrella defaults while preserving explicit environment overrides."""

    environment = os.environ.copy()
    for name, value in values.items():
        if value is None or value == "":
            continue
        rendered = str(value).lower() if isinstance(value, bool) else str(value)
        environment.setdefault(name, rendered)
    return environment

#!/usr/bin/env python3
"""Run the VyOS component with configuration inherited from the umbrella repo."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

from lab_config import (  # noqa: E402
    DEFAULT_CONFIG,
    LabConfigError,
    apply_environment,
    general_environment,
    load_config,
    mapping,
    resolve_from_root,
)


def environment_for(config: Mapping[str, Any]) -> tuple[dict[str, str], Path]:
    general = mapping(config, "general")
    vyos = mapping(config, "vyos")
    artifacts_root = resolve_from_root(general.get("artifacts_directory", "artifacts"))
    artifacts = artifacts_root / str(vyos.get("artifact_subdirectory", "vyos"))
    builder = resolve_from_root(vyos.get("builder_directory", "components/vyos-ova-builder"))

    inherited: dict[str, object] = {
        **general_environment(config),
        "VYOS_OVA_CONTENT_LIBRARY": general.get("content_library"),
        "VYOS_OVA_SOURCE_DIRECTORY": str(
            resolve_from_root(vyos.get("source_directory", "components/vyos-build"))
        ),
        "VYOS_OVA_SOURCE_BRANCH": vyos.get("source_branch", "rolling"),
        "VYOS_OVA_SOURCE_REVISION": vyos.get("source_revision"),
        "VYOS_OVA_ARTIFACTS_DIR": str(artifacts),
        "VYOS_OVA_BUILD_BY": vyos.get("build_by"),
        "VYOS_OVA_TEMPLATE_NAME": vyos.get("template_name"),
        "VYOS_OVA_NAME": vyos.get("ova_name"),
        "VYOS_OVA_DISPLAY_NAME": vyos.get("display_name"),
        "VYOS_OVA_CPUS": vyos.get("cpus"),
        "VYOS_OVA_MEMORY_MB": vyos.get("memory_mb"),
        "VYOS_OVA_NETWORK_ADAPTERS": vyos.get("network_adapters"),
        "VYOS_OVA_NETWORK_NAME": vyos.get("network_name"),
    }
    custom_packages = vyos.get("custom_packages")
    if isinstance(custom_packages, list):
        inherited["VYOS_OVA_CUSTOM_PACKAGES"] = ",".join(str(item) for item in custom_packages)

    return apply_environment(inherited), builder


def command_for(action: str, builder: Path) -> list[str]:
    commands = {
        "validate": ["python3", "scripts/project_config.py", "validate"],
        "validate-upload": ["python3", "scripts/project_config.py", "validate", "--upload"],
        "show": ["python3", "scripts/project_config.py", "show"],
        "test": ["make", "test"],
        "build": ["./build.sh"],
        "upload": ["./upload.sh"],
    }
    return commands[action]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action", choices=("validate", "validate-upload", "show", "test", "build", "upload")
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("NESTED_VCF_LAB_CONFIG", DEFAULT_CONFIG)),
        help="Umbrella configuration file",
    )
    args = parser.parse_args()

    try:
        config = load_config(args.config.expanduser().resolve())
        environment, builder = environment_for(config)
        if not (builder / "build.sh").is_file():
            raise LabConfigError(f"VyOS builder is missing or not initialized: {builder}")
        return subprocess.run(
            command_for(args.action, builder),
            cwd=builder,
            env=environment,
            check=False,
        ).returncode
    except LabConfigError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

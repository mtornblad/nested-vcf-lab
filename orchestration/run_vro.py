#!/usr/bin/env python3
"""Validate, test, package, and publish the separate vRO TypeScript component."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

from lab_config import DEFAULT_CONFIG, LabConfigError, load_config, mapping, resolve_from_root


PROFILE_ENVIRONMENT_VARIABLE = "VRO_PROFILE"
PROFILE_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


def orchestrator_settings(config: Mapping[str, Any]) -> Mapping[str, Any]:
    settings = config.get("orchestrator", {})
    if not isinstance(settings, Mapping):
        raise LabConfigError("orchestrator must be a JSON object")
    return settings


def resolve_profile(
    config: Mapping[str, Any],
    cli_profile: str | None = None,
    environment: Mapping[str, str] | None = None,
) -> tuple[str | None, str | None]:
    env = os.environ if environment is None else environment
    settings = orchestrator_settings(config)
    automation = config.get("automation", {})
    inherited = automation.get("maven_profile") if isinstance(automation, Mapping) else None
    for value, source in (
        (cli_profile, "command line"),
        (env.get(PROFILE_ENVIRONMENT_VARIABLE), PROFILE_ENVIRONMENT_VARIABLE),
        (settings.get("maven_profile"), "orchestrator.maven_profile"),
        (inherited, "automation.maven_profile"),
    ):
        if isinstance(value, str) and value.strip():
            profile = value.strip()
            if PROFILE_PATTERN.fullmatch(profile) is None:
                raise LabConfigError(f"Maven profile from {source} contains unsupported characters")
            return profile, source
    return None, None


def command_for(action: str, profile: str | None = None) -> list[str]:
    if action in {"pull", "download"}:
        raise LabConfigError(
            "TypeScript pull is unsupported: vRO JavaScript cannot be converted back "
            "to this TypeScript source. Use Git to retrieve source changes."
        )
    if action == "upload":
        if not profile or PROFILE_PATTERN.fullmatch(profile) is None:
            raise LabConfigError("Upload requires a valid Maven profile; configure orchestrator.maven_profile or --profile")
        return ["make", "push", f"PROFILE={profile}"]
    return ["make", {"validate": "validate", "test": "test", "build": "package", "clean": "clean"}[action]]


def artifact_directory(config: Mapping[str, Any]) -> Path:
    general = mapping(config, "general")
    root = resolve_from_root(general.get("artifacts_directory", "artifacts"))
    label = orchestrator_settings(config).get("artifact_subdirectory", "vro")
    if not isinstance(label, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", label):
        raise LabConfigError("orchestrator.artifact_subdirectory must be a single directory name")
    destination = (root / label / "builds").resolve()
    if not destination.is_relative_to(root):
        raise LabConfigError("Orchestrator output directory escapes the configured artifacts directory")
    return destination


def collect_packages(builder: Path, destination: Path) -> list[Path]:
    packages = sorted(path for path in (builder / "target").glob("*.package") if path.is_file())
    if not packages:
        raise LabConfigError("Maven completed without a .package file in the component target directory")
    destination.mkdir(parents=True, exist_ok=True)
    results: list[Path] = []
    for package in packages:
        output = destination / package.name
        if output.is_symlink():
            raise LabConfigError(f"Refusing to overwrite a symbolic link: {output}")
        shutil.copy2(package, output)
        results.append(output)
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("show", "validate", "test", "build", "upload", "clean", "pull", "download"))
    parser.add_argument("--config", type=Path, default=Path(os.environ.get("NESTED_VCF_LAB_CONFIG", DEFAULT_CONFIG)))
    parser.add_argument("--profile", help="Override VRO_PROFILE and the profile selected in umbrella configuration")
    args = parser.parse_args()
    try:
        # Explain the unsupported operation without requiring configuration or a checkout.
        if args.action in {"pull", "download"}:
            command_for(args.action)
        config = load_config(args.config.expanduser().resolve())
        settings = orchestrator_settings(config)
        builder = resolve_from_root(settings.get("builder_directory", "components/vro-typescript"))
        destination = artifact_directory(config)
        profile, source = resolve_profile(config, args.profile)
        if args.action == "show":
            print(json.dumps({
                "builder_directory": str(builder),
                "artifacts_directory": str(destination),
                "maven_profile": profile,
                "maven_profile_source": source,
                "source_pull_supported": False,
            }, indent=2))
            return 0
        if not (builder / "pom.xml").is_file() or not (builder / "Makefile").is_file():
            raise LabConfigError("vRO TypeScript component is missing; initialize components/vro-typescript first")
        command = command_for(args.action, profile)
        result = subprocess.run(command, cwd=builder, check=False)
        if result.returncode == 0 and args.action in {"build", "upload"}:
            for package in collect_packages(builder, destination):
                print(f"Package copied to {package}")
        return result.returncode
    except (LabConfigError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

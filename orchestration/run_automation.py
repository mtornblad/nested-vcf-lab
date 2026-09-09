#!/usr/bin/env python3
"""Pull, validate, package, and publish the VCF Automation blueprint component."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

from lab_config import (  # noqa: E402
    DEFAULT_CONFIG,
    LabConfigError,
    load_config,
    mapping,
    resolve_from_root,
)


PROFILE_ENVIRONMENT_VARIABLE = "VCFA_PROFILE"
PROFILE_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


def automation_settings(config: Mapping[str, Any]) -> tuple[Mapping[str, Any], Path]:
    settings = mapping(config, "automation")
    builder = resolve_from_root(
        settings.get("builder_directory", "components/vcf-automation")
    )
    return settings, builder


def resolve_profile(
    settings: Mapping[str, Any],
    cli_profile: str | None = None,
    environment: Mapping[str, str] | None = None,
) -> tuple[str, str]:
    """Resolve CLI, environment, then umbrella-config profile precedence."""

    env = os.environ if environment is None else environment
    candidates = (
        (cli_profile, "command line"),
        (env.get(PROFILE_ENVIRONMENT_VARIABLE), PROFILE_ENVIRONMENT_VARIABLE),
        (settings.get("maven_profile"), "automation.maven_profile"),
    )
    for value, source in candidates:
        if isinstance(value, str) and value.strip():
            profile = value.strip()
            if PROFILE_PATTERN.fullmatch(profile) is None:
                raise LabConfigError(
                    f"Maven profile from {source} contains unsupported characters: {profile!r}"
                )
            return profile, source
    raise LabConfigError(
        "No Maven profile is configured; set automation.maven_profile, "
        f"{PROFILE_ENVIRONMENT_VARIABLE}, or --profile."
    )


def command_for(
    action: str,
    profile: str,
    spec: Path | None = None,
    allow_secret_references: bool = False,
    force_pull: bool = False,
) -> list[str]:
    commands = {
        "validate": ["make", "validate"],
        "test": ["make", "test"],
        "build": ["make", "package"],
        "upload": ["make", "push", f"PROFILE={profile}"],
        "clean": ["make", "clean"],
    }
    if action in {"pull", "download"}:
        command = ["make", "pull", f"PROFILE={profile}"]
        if force_pull:
            command.append("FORCE=true")
        return command
    if action != "validate-spec":
        return commands[action]
    if spec is None:
        raise LabConfigError("--spec is required for validate-spec")
    command = ["python3", "scripts/validate_vcf_spec.py", str(spec)]
    if allow_secret_references:
        command.append("--allow-secret-references")
    return command


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "action",
        choices=(
            "show",
            "pull",
            "download",
            "validate",
            "validate-spec",
            "test",
            "build",
            "upload",
            "clean",
        ),
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(os.environ.get("NESTED_VCF_LAB_CONFIG", DEFAULT_CONFIG)),
        help="Umbrella configuration file",
    )
    parser.add_argument(
        "--profile",
        help=(
            "Maven settings profile override; takes precedence over "
            f"{PROFILE_ENVIRONMENT_VARIABLE} and umbrella configuration"
        ),
    )
    parser.add_argument(
        "--spec",
        type=Path,
        help="Rendered VCF deployment JSON (required for validate-spec)",
    )
    parser.add_argument(
        "--allow-secret-references",
        action="store_true",
        help="Allow encrypted VCF Automation references during structural JSON validation",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow pull/download to overwrite a dirty component checkout",
    )
    args = parser.parse_args()

    try:
        config = load_config(args.config.expanduser().resolve())
        settings, builder = automation_settings(config)
        profile, profile_source = resolve_profile(settings, args.profile)
        if args.force and args.action not in {"pull", "download"}:
            raise LabConfigError("--force is only valid with pull or download")
        if not (builder / "pom.xml").is_file() or not (builder / "Makefile").is_file():
            raise LabConfigError(
                f"VCF Automation component is missing or not initialized: {builder}"
            )

        if args.action == "show":
            print(
                json.dumps(
                    {
                        "builder_directory": str(builder),
                        "maven_profile": profile,
                        "maven_profile_source": profile_source,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        spec = args.spec.expanduser().resolve() if args.spec is not None else None
        return subprocess.run(
            command_for(
                args.action,
                profile,
                spec=spec,
                allow_secret_references=args.allow_secret_references,
                force_pull=args.force,
            ),
            cwd=builder,
            check=False,
        ).returncode
    except LabConfigError as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

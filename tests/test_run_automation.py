from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "orchestration"))

import run_automation  # noqa: E402
from lab_config import LabConfigError  # noqa: E402


class AutomationRunnerTests(unittest.TestCase):
    def test_example_configuration_defines_the_default_profile(self) -> None:
        config = json.loads(
            (PROJECT_ROOT / "configuration" / "lab.example.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual("lab", config["automation"]["maven_profile"])
        self.assertEqual(
            "components/vcf-automation",
            config["automation"]["builder_directory"],
        )

    def test_profile_precedence_is_cli_then_environment_then_config(self) -> None:
        settings = {"maven_profile": "config-profile"}

        self.assertEqual(
            ("cli-profile", "command line"),
            run_automation.resolve_profile(
                settings,
                "cli-profile",
                {run_automation.PROFILE_ENVIRONMENT_VARIABLE: "environment-profile"},
            ),
        )
        self.assertEqual(
            ("environment-profile", run_automation.PROFILE_ENVIRONMENT_VARIABLE),
            run_automation.resolve_profile(
                settings,
                environment={run_automation.PROFILE_ENVIRONMENT_VARIABLE: "environment-profile"},
            ),
        )
        self.assertEqual(
            ("config-profile", "automation.maven_profile"),
            run_automation.resolve_profile(settings, environment={}),
        )

    def test_invalid_profile_is_rejected(self) -> None:
        with self.assertRaisesRegex(LabConfigError, "unsupported characters"):
            run_automation.resolve_profile(
                {"maven_profile": "lab;unexpected"},
                environment={},
            )

    def test_component_actions_map_to_the_supported_make_contract(self) -> None:
        self.assertEqual(["make", "validate"], run_automation.command_for("validate", "lab"))
        self.assertEqual(["make", "test"], run_automation.command_for("test", "lab"))
        self.assertEqual(["make", "package"], run_automation.command_for("build", "lab"))
        self.assertEqual(
            ["make", "push", "PROFILE=override"],
            run_automation.command_for("upload", "override"),
        )

    def test_validate_spec_forwards_the_structural_secret_mode(self) -> None:
        spec = Path("/tmp/vcf-deployment.json")

        self.assertEqual(
            [
                "python3",
                "scripts/validate_vcf_spec.py",
                str(spec),
                "--allow-secret-references",
            ],
            run_automation.command_for(
                "validate-spec",
                "lab",
                spec=spec,
                allow_secret_references=True,
            ),
        )

    def test_validate_spec_requires_a_path(self) -> None:
        with self.assertRaisesRegex(LabConfigError, "--spec"):
            run_automation.command_for("validate-spec", "lab")


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "orchestration"))

import run_vro  # noqa: E402
from lab_config import LabConfigError  # noqa: E402


class VroRunnerTests(unittest.TestCase):
    def test_profile_precedence_and_automation_inheritance(self) -> None:
        config = {"orchestrator": {"maven_profile": "vro"}, "automation": {"maven_profile": "shared"}}
        self.assertEqual(("cli", "command line"), run_vro.resolve_profile(config, "cli", {"VRO_PROFILE": "env"}))
        self.assertEqual(("env", "VRO_PROFILE"), run_vro.resolve_profile(config, environment={"VRO_PROFILE": "env"}))
        self.assertEqual(("vro", "orchestrator.maven_profile"), run_vro.resolve_profile(config, environment={}))
        del config["orchestrator"]
        self.assertEqual(("shared", "automation.maven_profile"), run_vro.resolve_profile(config, environment={}))

    def test_build_needs_no_target_profile(self) -> None:
        self.assertEqual((None, None), run_vro.resolve_profile({}, environment={}))
        self.assertEqual(["make", "package"], run_vro.command_for("build"))
        self.assertEqual(["make", "test"], run_vro.command_for("test"))

    def test_upload_requires_a_valid_profile(self) -> None:
        self.assertEqual(["make", "push", "PROFILE=lab"], run_vro.command_for("upload", "lab"))
        for profile in (None, "lab;unexpected", "lab -DskipTests=true"):
            with self.subTest(profile=profile), self.assertRaises(LabConfigError):
                run_vro.command_for("upload", profile)
        with self.assertRaises(LabConfigError):
            run_vro.resolve_profile({}, "bad profile", {})

    def test_pull_and_download_are_explicitly_unsupported(self) -> None:
        for action in ("pull", "download"):
            with self.subTest(action=action), self.assertRaisesRegex(LabConfigError, "TypeScript pull is unsupported"):
                run_vro.command_for(action)

    def test_artifact_path_stays_inside_the_configured_root(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "artifacts"
            config = {"general": {"artifacts_directory": str(root)}, "orchestrator": {"artifact_subdirectory": "vro"}}
            self.assertEqual(root / "vro" / "builds", run_vro.artifact_directory(config))
            config["orchestrator"]["artifact_subdirectory"] = "../outside"
            with self.assertRaises(LabConfigError):
                run_vro.artifact_directory(config)
            config["orchestrator"]["artifact_subdirectory"] = "vro"
            root.mkdir()
            (root / "vro").symlink_to(directory, target_is_directory=True)
            with self.assertRaises(LabConfigError):
                run_vro.artifact_directory(config)

    def test_copies_only_packaged_output(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            builder = root / "component"
            (builder / "target").mkdir(parents=True)
            (builder / "target" / "lab.package").write_bytes(b"package-content")
            (builder / "target" / "build.log").write_text("not an artifact")
            destination = root / "artifacts"
            result = run_vro.collect_packages(builder, destination)
            self.assertEqual([destination / "lab.package"], result)
            self.assertEqual(b"package-content", result[0].read_bytes())
            self.assertFalse((destination / "build.log").exists())

    def test_missing_package_is_not_reported_as_a_successful_build(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(LabConfigError, "without a .package"):
                run_vro.collect_packages(root, root / "artifacts")

    def test_existing_symlink_is_not_overwritten_by_collection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "target").mkdir()
            (root / "target" / "lab.package").write_bytes(b"new")
            target = root / "private"
            target.write_bytes(b"keep")
            destination = root / "artifacts"
            destination.mkdir()
            (destination / "lab.package").symlink_to(target)
            with self.assertRaises(LabConfigError):
                run_vro.collect_packages(root, destination)
            self.assertEqual(b"keep", target.read_bytes())


if __name__ == "__main__":
    unittest.main()

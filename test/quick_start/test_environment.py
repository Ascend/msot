"""Host-only checks: these do not validate CANN or device execution."""
import importlib.util
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "example/quick_start/scripts"
TIMESTAMP = "2026-11-10 01:35:10"


def temporary_directory(prefix):
    base = Path(os.environ["LOCALAPPDATA"]) / "Temp/opencode" if os.name == "nt" else None
    if base is not None:
        base.mkdir(parents=True, exist_ok=True)
    return tempfile.TemporaryDirectory(prefix=prefix, dir=base)


def load_helpers():
    if str(SCRIPTS) not in sys.path:
        sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location("quick_start_helpers", SCRIPTS / "_helpers.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EnvironmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = load_helpers()

    def test_core_reports_every_failure_and_returns_nonzero(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
                mock.patch.object(Path, "is_file", return_value=False), \
                mock.patch.object(Path, "is_dir", return_value=False), \
                mock.patch.object(shutil, "which", return_value=None), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(self.helpers.check_environment("core"), 1)
        self.assertEqual(output.getvalue().count("[FAIL]"), 9)
        self.assertEqual(output.getvalue().count("; reason: "), 9)
        self.assertIn("[INFO] Starting to check the environment...", output.getvalue())
        self.assertNotIn("Prerequisite checks only", output.getvalue())
        self.assertIn("[ERROR] Environment check failed, summary 9 failure(s).", output.getvalue())
        for reason in ("container marker is missing; please run inside the documented CANN container.",
                       "variable is unset or empty; please configure it using the installation guide.",
                       "required sample files are missing; please use a complete msOT checkout.",
                       "command not found in PATH; please check the CANN installation and environment setup."):
            self.assertIn(reason, output.getvalue())
        self.assertEqual(output.getvalue().count("; please "), 9)
        self.assertEqual(output.getvalue().count("[ERROR]"), 10)
        self.assertEqual(output.getvalue().count("[INFO]"), 1)
        for line in output.getvalue().splitlines():
            plain = re.sub(r"\033\[[0-9;]*m", "", line)
            self.assertRegex(plain, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \[(INFO|ERROR)\] ")

    def test_whitespace_only_variables_explain_failure(self):
        env = {key: " \t" for key in ("ASCEND_HOME_PATH", "ATB_HOME_PATH", "MY_STUDY_VAR_CHIP_SOC_TYPE")}
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(Path, "is_file", return_value=True), \
                mock.patch.object(Path, "is_dir", return_value=True), \
                mock.patch.object(shutil, "which", return_value="/tools/command"), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(self.helpers.check_environment("core"), 1)
        self.assertEqual(output.getvalue().count("[FAIL]"), 3)
        self.assertEqual(output.getvalue().count("; reason: variable is unset or empty"), 3)
        self.assertEqual(output.getvalue().count("[ERROR]"), 4)
        self.assertIn("[ERROR] Environment check failed, summary 3 failure(s).", output.getvalue())

    def test_core_success_checks_command_existence_without_running_tools(self):
        env = {key: "configured" for key in ("ASCEND_HOME_PATH", "ATB_HOME_PATH", "MY_STUDY_VAR_CHIP_SOC_TYPE")}
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(Path, "is_file", return_value=True), \
                mock.patch.object(Path, "is_dir", return_value=True), \
                mock.patch.object(shutil, "which", return_value="/tools/command"), \
                mock.patch.object(subprocess, "run") as run, \
                mock.patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(self.helpers.check_environment("core"), 0)
            run.assert_not_called()
        self.assertNotIn("; reason:", output.getvalue())
        self.assertNotIn("\033[", output.getvalue())
        self.assertNotIn("[ERROR]", output.getvalue())
        self.assertEqual(output.getvalue().count("[INFO]"), 11)
        self.assertIn("[INFO] Environment check successful, summary 0 failure(s).", output.getvalue())

    def probe(self, text="", returncode=0):
        result = subprocess.CompletedProcess(["npu-smi", "info", "-m"], returncode, text, "diagnostic")
        with mock.patch.object(shutil, "which", return_value="/tools/npu-smi"), \
                mock.patch.object(subprocess, "run", return_value=result), \
                mock.patch.object(self.helpers, "datetime") as clock, \
                mock.patch("sys.stdout", new_callable=io.StringIO) as output:
            clock.now.return_value.strftime.return_value = TIMESTAMP
            code = self.helpers.check_environment("mskpp")
        return code, output.getvalue()

    def test_supported_chip_and_model_suffix(self):
        for text in ("Chip Name : Ascend 910B", "Chip Name : Ascend 910B2", "Chip Name : Ascend910B4"):
            with self.subTest(text=text):
                code, output = self.probe(text)
                self.assertEqual(code, 0)
                self.assertIn("910B meets the requirements.", output)

    def test_repeated_chip_models_are_reported_once(self):
        for model, code, message in (("910B2", 0, "910B meets the requirements."),
                                     ("310P", 1, "unsupported for this msKPP tutorial; reason: "
                                      "this msKPP tutorial requires Ascend 910B-series chips")):
            with self.subTest(model=model):
                status, output = self.probe("\n".join(["Ascend " + model] * 8))
                self.assertEqual(status, code)
                prefix = "PASS" if code == 0 else "FAIL"
                color = "" if code == 0 else "\033[31m"
                reset = "" if code == 0 else "\033[0m"
                level = "INFO" if code == 0 else "ERROR"
                line = "{}{} [{}] [{}] detected chips: {}; {}{}".format(
                    color, TIMESTAMP, level, prefix, model, message, reset)
                self.assertIn(line, output.splitlines())
                result = "successful" if code == 0 else "failed"
                self.assertIn("Environment check {}, summary {} failure(s).".format(result, code), output)

    def test_distinct_models_keep_first_seen_order(self):
        for text, code, message in (
                ("Ascend 910B4\nAscend 910B2\nAscend 910B4", 0,
                 "[PASS] detected chips: 910B4, 910B2; 910B meets the requirements."),
                ("Ascend 310P\nAscend 910B2\nAscend 310P\nAscend 910B2", 1,
                 "[FAIL] detected chips: 310P, 910B2; unsupported for this msKPP tutorial; reason: "
                 "this msKPP tutorial requires Ascend 910B-series chips")):
            with self.subTest(text=text):
                status, output = self.probe(text)
                self.assertEqual(status, code)
                color = "" if code == 0 else "\033[31m"
                reset = "" if code == 0 else "\033[0m"
                level = "INFO" if code == 0 else "ERROR"
                self.assertIn("{}{} [{}] {}{}".format(color, TIMESTAMP, level, message, reset), output.splitlines())

    def test_status_colors_are_reset_before_summary(self):
        for text, code, color in (("Ascend 910B2", 0, ""),
                                   ("Ascend 310P", 1, "\033[31m"),
                                   ("", 1, "\033[31m")):
            with self.subTest(text=text):
                status, output = self.probe(text)
                self.assertEqual(status, code)
                lines = output.splitlines()
                level = "INFO" if code == 0 else "ERROR"
                status = "PASS" if code == 0 else "FAIL"
                self.assertEqual(lines[0], TIMESTAMP + " [INFO] Starting to check the environment...")
                self.assertTrue(lines[1].startswith("{}{} [{}] [{}] ".format(color, TIMESTAMP, level, status)))
                if code == 0:
                    self.assertNotIn("\033[", output)
                else:
                    self.assertTrue(lines[1].endswith("\033[0m"))
                result = "successful" if code == 0 else "failed"
                self.assertEqual(lines[2], "{} [{}] Environment check {}, summary {} failure(s).".format(
                    TIMESTAMP, level, result, code))

    def test_unsupported_chip_is_not_probe_failure(self):
        code, output = self.probe("Chip Name : Ascend 310P")
        self.assertEqual(code, 1)
        self.assertIn("unsupported", output)

    def test_empty_output_and_nonzero_are_probe_failures(self):
        for text, code, reason in (("", 0, "no recognized Ascend chip model"),
                                   ("unparseable", 0, "no recognized Ascend chip model"),
                                   ("Ascend 910B", 1, "npu-smi exited with code 1")):
            with self.subTest(text=text, code=code):
                status, output = self.probe(text, code)
                self.assertEqual(status, 1)
                self.assertIn("probe failed", output)
                self.assertIn("; reason: " + reason, output)

    def test_multiple_devices_must_all_be_supported(self):
        self.assertEqual(self.probe("Ascend 910B2\nAscend 310P")[0], 1)

    def test_chip_boundary_does_not_accept_unrecognized_suffix(self):
        self.assertEqual(self.probe("Ascend 910Bad")[0], 1)

    def test_missing_or_failing_probe(self):
        with mock.patch.object(shutil, "which", return_value=None), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as output:
            self.assertEqual(self.helpers.check_environment("mskpp"), 1)
        self.assertIn("; reason: npu-smi was not found in PATH", output.getvalue())
        for error, reason in ((OSError("unavailable"), "could not execute npu-smi: unavailable"),
                              (subprocess.TimeoutExpired("npu-smi", 15), "npu-smi did not respond within 15 seconds")):
            with mock.patch.object(shutil, "which", return_value="npu-smi"), \
                    mock.patch.object(subprocess, "run", side_effect=error), \
                    mock.patch("sys.stdout", new_callable=io.StringIO) as output:
                self.assertEqual(self.helpers.check_environment("mskpp"), 1)
            self.assertIn("; reason: " + reason, output.getvalue())

    def test_real_path_probe_stub_without_device(self):
        with temporary_directory("msot chip stub ") as directory:
            stub = Path(directory) / ("npu-smi.cmd" if os.name == "nt" else "npu-smi")
            for model in ("910B2", "310P"):
                if os.name == "nt":
                    stub.write_bytes(("@echo off\r\necho Chip Name : Ascend " + model + "\r\n").encode("ascii"))
                else:
                    stub.write_text("#!/bin/sh\nprintf 'Chip Name : Ascend " + model + "\\n'\n", encoding="utf-8")
                    stub.chmod(0o755)
                with mock.patch.dict(os.environ, {"PATH": directory}), \
                        mock.patch("sys.stdout", new_callable=io.StringIO) as output:
                    code = self.helpers.check_environment("mskpp")
                self.assertEqual(code, int(model != "910B2"), output.getvalue())


@unittest.skipUnless(shutil.which("bash"), "Bash is required for entry-point tests")
class EnvironmentEntryTests(unittest.TestCase):
    def run_script(self, *args):
        return subprocess.run([shutil.which("bash"), (SCRIPTS / "check_env.sh").as_posix(), *args],
                              capture_output=True, text=True, encoding="utf-8", timeout=30)

    def test_help(self):
        result = self.run_script("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--task", result.stdout)

    def test_invalid_arguments(self):
        for args in ((), ("--task", "unknown"), ("--task", "core", "--force")):
            with self.subTest(args=args):
                result = self.run_script(*args)
                self.assertNotEqual(result.returncode, 0)
                self.assertNotIn("Traceback", result.stderr)

    def test_real_core_entry_fails_when_required_variables_are_missing(self):
        env = dict(os.environ)
        for name in ("ASCEND_HOME_PATH", "ATB_HOME_PATH", "MY_STUDY_VAR_CHIP_SOC_TYPE"):
            env.pop(name, None)
        result = subprocess.run([shutil.which("bash"), (SCRIPTS / "check_env.sh").as_posix(), "--task", "core"],
                                env=env, capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("[FAIL] environment variable ASCEND_HOME_PATH", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()

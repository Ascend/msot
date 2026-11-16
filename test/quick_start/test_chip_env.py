"""Host-only tests for sourced SoC setup; never write the system profile."""
import io
import errno
import os
from pathlib import Path
import shutil
import subprocess
import sys
import unittest
from unittest import mock

from test_environment import SCRIPTS, load_helpers, temporary_directory


class ChipEnvironmentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_helpers()
        import _chip_env
        cls.chip_env = _chip_env

    def test_query_preserves_model_case_and_suffix(self):
        for model in ("910B2", "310P3", "910_9391", "910B4-1"):
            with self.subTest(model=model):
                result = subprocess.CompletedProcess([], 0, "Ascend" + model + "\n", "")
                with mock.patch.object(subprocess, "run", return_value=result) as run:
                    self.assertEqual(self.chip_env.query_chip_soc(), model)
                self.assertEqual(run.call_args.args[0][0], sys.executable)
                self.assertEqual(run.call_args.kwargs["timeout"], 15)

    def test_empty_unknown_or_injected_model_is_rejected(self):
        for output in ("", "Ascend", "910B2", "Ascend910B2\nAscend310P", "Ascend910B2; echo unsafe"):
            with self.subTest(output=output):
                result = subprocess.CompletedProcess([], 0, output, "")
                with mock.patch.object(subprocess, "run", return_value=result):
                    with self.assertRaisesRegex(self.chip_env.PreparationError, "empty or unrecognized"):
                        self.chip_env.query_chip_soc()

    def test_query_failures_explain_reason(self):
        result = subprocess.CompletedProcess([], 1, "", "ModuleNotFoundError: No module named 'acl'\n")
        with mock.patch.object(subprocess, "run", return_value=result):
            with self.assertRaisesRegex(self.chip_env.PreparationError, "No module named 'acl'"):
                self.chip_env.query_chip_soc()
        for error, message in ((subprocess.TimeoutExpired("python3", 15), "timed out"),
                               (OSError("unavailable"), "Could not start")):
            with self.subTest(error=error), mock.patch.object(subprocess, "run", side_effect=error):
                with self.assertRaisesRegex(self.chip_env.PreparationError, message):
                    self.chip_env.query_chip_soc()

    def test_session_only_prints_value_without_profile_access(self):
        with mock.patch.object(self.chip_env, "query_chip_soc", return_value="910B2"), \
                mock.patch.object(self.chip_env, "persist_profile") as persist, \
                mock.patch.object(Path, "open", side_effect=AssertionError("No profile access expected")), \
                mock.patch.object(os, "open", side_effect=AssertionError("No lock creation expected")), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as output, \
                mock.patch("sys.stderr", new_callable=io.StringIO) as errors:
            self.assertEqual(self.chip_env.main(["--session-only"]), 0)
        persist.assert_not_called()
        self.assertEqual(output.getvalue(), "910B2\n")
        self.assertEqual(errors.getvalue(), "")

    def test_profile_creation_and_identical_reuse_need_no_further_write(self):
        with temporary_directory("msot-chip-profile-") as directory:
            path = Path(directory) / "custom-env.sh"
            self.chip_env.persist_profile(path)
            modified = path.stat().st_mtime_ns
            with mock.patch.object(self.chip_env, "directory_lock", side_effect=PermissionError("not writable")) as lock:
                self.chip_env.persist_profile(path)
            lock.assert_not_called()
            self.assertEqual(path.read_bytes(), self.chip_env.PROFILE_CONTENT)
            self.assertEqual(path.stat().st_mtime_ns, modified)
            self.assertEqual(sorted(p.name for p in Path(directory).iterdir()), ["custom-env.sh"])

    def test_profile_conflict_is_detected_before_acquiring_a_write_lock(self):
        with temporary_directory("msot-chip-conflict-") as directory:
            path = Path(directory) / "custom-env.sh"
            path.write_text("# user's configuration\n")
            with mock.patch.object(self.chip_env, "directory_lock", side_effect=PermissionError("not writable")) as lock:
                with self.assertRaisesRegex(self.chip_env.PreparationError, "conflict"):
                    self.chip_env.persist_profile(path)
            lock.assert_not_called()
            self.assertEqual(path.read_text(), "# user's configuration\n")

    def test_pending_or_locked_profile_is_not_adopted_even_when_identical(self):
        with temporary_directory("msot-chip-pending-") as directory:
            path = Path(directory) / "custom-env.sh"
            path.write_bytes(self.chip_env.PROFILE_CONTENT)
            for name, message in ((".msot-chip-env-pending.json", "Unfinished"),
                                   (".msot-prepare.lock", "lock")):
                with self.subTest(name=name):
                    marker = path.parent / name
                    marker.write_text("another or interrupted operation")
                    with self.assertRaisesRegex(self.chip_env.PreparationError, message):
                        self.chip_env.persist_profile(path)
                    self.assertTrue(marker.exists())
                    marker.unlink()

    def test_permission_and_readonly_filesystem_errors_fall_back_with_warning(self):
        for error in (PermissionError(errno.EACCES, "Permission denied"),
                      PermissionError(errno.EPERM, "Operation not permitted"),
                      OSError(errno.EROFS, "Read-only file system")):
            with self.subTest(error=error), \
                    mock.patch.object(self.chip_env, "query_chip_soc", return_value="910B2"), \
                    mock.patch.object(self.chip_env, "persist_profile", side_effect=error), \
                    mock.patch("sys.stdout", new_callable=io.StringIO) as output, \
                    mock.patch("sys.stderr", new_callable=io.StringIO) as errors:
                self.assertEqual(self.chip_env.main([]), 0)
            self.assertEqual(output.getvalue(), "910B2\n")
            self.assertIn("[WARNING]", errors.getvalue())
            self.assertIn("current-session setup only", errors.getvalue())
            self.assertNotIn("[ERROR]", errors.getvalue())

    def test_other_persistence_errors_remain_fatal(self):
        for error in (OSError(errno.ENOSPC, "No space left on device"),
                      self.chip_env.PreparationError("File conflict")):
            with self.subTest(error=error), \
                    mock.patch.object(self.chip_env, "query_chip_soc", return_value="910B2"), \
                    mock.patch.object(self.chip_env, "persist_profile", side_effect=error), \
                    mock.patch("sys.stdout", new_callable=io.StringIO) as output, \
                    mock.patch("sys.stderr", new_callable=io.StringIO) as errors:
                self.assertEqual(self.chip_env.main([]), 1)
            self.assertEqual(output.getvalue(), "")
            self.assertIn("[ERROR]", errors.getvalue())
            self.assertNotIn("[WARNING]", errors.getvalue())

    def test_default_setup_reports_profile_and_prints_only_validated_value(self):
        with mock.patch.object(self.chip_env, "query_chip_soc", return_value="910B2"), \
                mock.patch.object(self.chip_env, "persist_profile") as persist, \
                mock.patch("sys.stdout", new_callable=io.StringIO) as output, \
                mock.patch("sys.stderr", new_callable=io.StringIO) as errors:
            self.assertEqual(self.chip_env.main([]), 0)
        persist.assert_called_once_with(self.chip_env.PROFILE_FILE)
        self.assertEqual(output.getvalue(), "910B2\n")
        self.assertIn("[INFO] Environment configuration is available at:", errors.getvalue())

    def test_query_failure_does_not_print_a_value(self):
        with mock.patch.object(self.chip_env, "query_chip_soc", side_effect=self.chip_env.PreparationError("acl unavailable")), \
                mock.patch("sys.stdout", new_callable=io.StringIO) as output, \
                mock.patch("sys.stderr", new_callable=io.StringIO) as errors:
            self.assertEqual(self.chip_env.main([]), 1)
        self.assertEqual(output.getvalue(), "")
        self.assertRegex(errors.getvalue(), r"\033\[31m\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \[ERROR\]")
        self.assertIn("acl unavailable", errors.getvalue())
        self.assertNotIn("Traceback", errors.getvalue())


@unittest.skipUnless(shutil.which("bash"), "Bash required")
class ChipEnvironmentSourceTests(unittest.TestCase):
    def setUp(self):
        self.temp = temporary_directory("msot chip source ")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.profile = self.directory / "profile/custom-env.sh"
        self.env = dict(os.environ, PYTHONPATH=str(self.directory), MY_STUDY_VAR_CHIP_SOC_TYPE="previous",
                        TEST_CHIP_PROFILE=str(self.profile), PYTHONDONTWRITEBYTECODE="1")
        self.acl = self.directory / "acl.py"
        self.acl.write_text('def get_soc_name():\n    return "Ascend910B2"\n', encoding="utf-8")
        self.script = SCRIPTS / "set_chip_soc_env.sh"
        # The sourced entry uses this shim only for the private helper. All profile
        # writes stay under the test directory, never /etc/profile.d.
        bin_dir = self.directory / "bin"
        bin_dir.mkdir()
        shim = bin_dir / "python3"
        shim.write_text("#!" + sys.executable + "\n"
                        "import errno,os,sys\nfrom pathlib import Path\n"
                        "sys.dont_write_bytecode = True\n"
                        "if len(sys.argv) > 2 and Path(sys.argv[2]).name == '_chip_env.py':\n"
                        "    sys.path.insert(0, " + repr(str(SCRIPTS)) + ")\n"
                        "    import _chip_env\n"
                        "    _chip_env.PROFILE_FILE = Path(os.environ['TEST_CHIP_PROFILE'])\n"
                        "    if os.environ.get('TEST_CHIP_DENY_PERSIST'):\n"
                        "        def denied(path):\n"
                        "            raise PermissionError(errno.EACCES, 'Permission denied', str(path))\n"
                        "        _chip_env.persist_profile = denied\n"
                        "    sys.exit(_chip_env.main(sys.argv[3:]))\n"
                        "os.execv(sys.executable, [sys.executable, *sys.argv[1:]])\n", encoding="utf-8")
        shim.chmod(0o755)
        self.env["PATH"] = str(bin_dir) + os.pathsep + self.env["PATH"]

    def source(self, *args, env=None, preamble=""):
        command = (preamble + '\nscript=$1\nshift\nsource "$script" "$@"\nstatus=$?\n'
                   'printf "PARENT_ALIVE=%s\\n" "$status"\n'
                   'printf "CHIP_VALUE=%s\\n" "$MY_STUDY_VAR_CHIP_SOC_TYPE"\n'
                   'exit "$status"')
        return subprocess.run([shutil.which("bash"), "-c", command, "bash", str(self.script), *args],
                              cwd=self.directory, env=env or self.env, capture_output=True,
                              text=True, timeout=30)

    def test_source_exports_to_parent_and_child_without_changing_shell_options(self):
        command = ('script=$1\nshift\nset -u\nbefore=$-\nsource "$script" || exit $?\n'
                   '[[ "$before" == "$-" ]] || exit 9\n'
                   'printf "CHIP_VALUE=%s\\n" "$MY_STUDY_VAR_CHIP_SOC_TYPE"\n'
                   'python3 -B -c \'import os; print("CHILD_VALUE=" + os.environ["MY_STUDY_VAR_CHIP_SOC_TYPE"])\'\n'
                   'if declare -F _msot_set_chip_soc_env >/dev/null; then exit 8; fi')
        result = subprocess.run([shutil.which("bash"), "-c", command, "bash", str(self.script)],
                                cwd=self.directory, env=self.env, capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CHIP_VALUE=910B2", result.stdout)
        self.assertIn("CHILD_VALUE=910B2", result.stdout)
        self.assertRegex(result.stdout, r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \[INFO\] Environment variable set successfully:")
        self.assertNotIn("\033[", result.stdout)

    def test_failed_query_keeps_old_value_and_parent_shell_alive(self):
        for body in ('raise ImportError("acl unavailable")\n',
                     'def get_soc_name():\n    return ""\n',
                     'def get_soc_name():\n    return "Ascend910B2; echo unsafe"\n'):
            with self.subTest(body=body):
                self.acl.write_text(body, encoding="utf-8")
                result = self.source()
                self.assertEqual(result.returncode, 1)
                self.assertIn("PARENT_ALIVE=1", result.stdout)
                self.assertIn("CHIP_VALUE=previous", result.stdout)
                self.assertIn("[ERROR]", result.stderr)
                self.assertNotIn("set successfully", result.stdout)

    def test_session_only_is_repeatable_without_creating_configuration_files(self):
        before = sorted(p.relative_to(self.directory) for p in self.directory.rglob("*"))
        for _ in range(2):
            result = self.source("--session-only")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("CHIP_VALUE=910B2", result.stdout)
            self.assertNotIn("configuration is available", result.stderr)
        self.assertEqual(sorted(p.relative_to(self.directory) for p in self.directory.rglob("*")), before)

    def test_explicit_session_only_does_not_create_a_profile(self):
        result = self.source("--session-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CHIP_VALUE=910B2", result.stdout)
        self.assertNotIn("configuration is available", result.stderr)
        self.assertFalse(self.profile.exists())

    def test_default_source_creates_and_reuses_profile(self):
        result = self.source()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CHIP_VALUE=910B2", result.stdout)
        self.assertTrue(self.profile.is_file())
        modified = self.profile.stat().st_mtime_ns
        result = self.source()
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.profile.stat().st_mtime_ns, modified)
        login = subprocess.run([shutil.which("bash"), "-c", 'source "$1"\nprintf "%s" "$MY_STUDY_VAR_CHIP_SOC_TYPE"',
                                "bash", str(self.profile)], cwd=self.directory, env=self.env,
                               capture_output=True, text=True, timeout=30)
        self.assertEqual(login.returncode, 0, login.stderr)
        self.assertEqual(login.stdout, "910B2")

    def test_no_write_permission_warns_but_sets_parent_variable(self):
        result = self.source(env={**self.env, "TEST_CHIP_DENY_PERSIST": "1"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("[WARNING]", result.stderr)
        self.assertIn("CHIP_VALUE=910B2", result.stdout)
        self.assertFalse(self.profile.exists())

    def test_profile_conflict_fails_without_overwriting_profile_or_variable(self):
        self.profile.parent.mkdir()
        self.profile.write_text("# user's configuration\n")
        result = self.source()
        self.assertEqual(result.returncode, 1)
        self.assertIn("[ERROR]", result.stderr)
        self.assertIn("File conflict", result.stderr)
        self.assertNotIn("[WARNING]", result.stderr)
        self.assertIn("CHIP_VALUE=previous", result.stdout)
        self.assertEqual(self.profile.read_text(), "# user's configuration\n")
        result = self.source("--session-only")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("CHIP_VALUE=910B2", result.stdout)
        self.assertEqual(self.profile.read_text(), "# user's configuration\n")

    def test_missing_python_reports_error_without_exiting_parent(self):
        bin_dir = self.directory / "no-python"
        bin_dir.mkdir()
        date = shutil.which("date")
        if date is None:
            self.skipTest("date required")
        (bin_dir / "date").symlink_to(date)
        result = self.source(env={**self.env, "PATH": str(bin_dir)})
        self.assertEqual(result.returncode, 1)
        self.assertIn("Python 3 is required", result.stderr)
        self.assertIn("PARENT_ALIVE=1", result.stdout)
        self.assertIn("CHIP_VALUE=previous", result.stdout)

    def test_help_and_invalid_arguments_do_not_change_variable(self):
        result = self.source("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Usage: source set_chip_soc_env.sh", result.stdout)
        self.assertIn("Without write permission", result.stdout)
        self.assertIn("--session-only", result.stdout)
        self.assertIn("CHIP_VALUE=previous", result.stdout)
        result = self.source("--unknown")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Unknown argument", result.stderr)
        self.assertIn("CHIP_VALUE=previous", result.stdout)

    def test_direct_execution_is_rejected(self):
        result = subprocess.run([shutil.which("bash"), str(self.script)], env=self.env,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 1)
        self.assertIn("must be sourced", result.stderr)

    def test_readonly_variable_is_rejected_without_changing_value(self):
        result = self.source(preamble="readonly MY_STUDY_VAR_CHIP_SOC_TYPE=previous")
        self.assertEqual(result.returncode, 1)
        self.assertIn("is readonly", result.stderr)
        self.assertIn("PARENT_ALIVE=1", result.stdout)
        self.assertIn("CHIP_VALUE=previous", result.stdout)


if __name__ == "__main__":
    unittest.main()

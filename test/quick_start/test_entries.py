import os
from pathlib import Path
import re
import shutil
import subprocess
import unittest

from test_environment import SCRIPTS, temporary_directory
from test_project import make_project


PREPARATION_SCRIPTS = sorted(script for script in SCRIPTS.glob("*.sh")
                             if script.name != "set_chip_soc_env.sh")


@unittest.skipUnless(shutil.which("bash"), "Bash required")
class EntryTests(unittest.TestCase):
    def run_script(self, script, *args, cwd=None, env=None):
        return subprocess.run([shutil.which("bash"), script, *args], cwd=cwd, env=env,
                              capture_output=True, text=True, encoding="utf-8", timeout=30)

    def test_all_five_help_and_missing_arguments_from_script_directory(self):
        scripts = PREPARATION_SCRIPTS
        self.assertEqual(len(scripts), 5)
        for script in scripts:
            with self.subTest(script=script.name):
                result = self.run_script(script.name, "--help", cwd=SCRIPTS)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("--", result.stdout)
                self.assertIn("bash " + script.name, result.stdout)
                result = self.run_script(script.name, cwd=SCRIPTS)
                self.assertEqual(result.returncode, 2, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_all_five_report_missing_python_without_traceback(self):
        with temporary_directory("msot no python ") as directory:
            env = {**os.environ, "PATH": directory}
            for script in PREPARATION_SCRIPTS:
                with self.subTest(script=script.name):
                    result = self.run_script(script.as_posix(), "--help", env=env)
                    self.assertEqual(result.returncode, 1, result.stderr)
                    self.assertIn("Python 3 is required", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_full_shell_preparation_lifecycle_with_spaces(self):
        with temporary_directory("msot complete shell ") as directory:
            project = make_project(Path(directory) / "space in parent/AddCustom")
            for script, args in (("prepare_add_demo.sh", []),
                                 ("prepare_mode.sh", ["--mode", "sanitizer", "--fixture", "oob"]),
                                 ("restore_demo.sh", []),
                                 ("prepare_mode.sh", ["--mode", "debug"]),
                                 ("restore_demo.sh", []),
                                 ("prepare_mode.sh", ["--mode", "profile"]),
                                 ("restore_demo.sh", [])):
                with self.subTest(script=script, args=args):
                    result = self.run_script((SCRIPTS / script).as_posix(), "--project", project.as_posix(),
                                             *args, cwd=directory)
                    self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse((project / "build_out").exists())
            self.assertFalse((project.parent / "caller/build").exists())

    def test_debug_symbol_message_has_timestamp_and_info_prefix(self):
        with temporary_directory("msot-debug-symbols-") as directory:
            obj = Path(directory) / "AddCustom_test.o"
            obj.write_bytes(b"test object")
            script = SCRIPTS.parent / "msdebug/set_kernel_obj_env.sh"
            result = self.run_script("-c", 'source "$1" "$2" || exit $?\n'
                                     'printf "LAUNCH_KERNEL_PATH=%s\\n" "$LAUNCH_KERNEL_PATH"',
                                     "bash", script.as_posix(), directory)
            self.assertEqual(result.returncode, 0, result.stderr)
            lines = result.stdout.splitlines()
            self.assertEqual(len(lines), 2)
            self.assertRegex(lines[0], r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \[INFO\] "
                             r"Find obj file, exec cmd:export LAUNCH_KERNEL_PATH=" + re.escape(str(obj)) + "$")
            self.assertEqual(lines[1], "LAUNCH_KERNEL_PATH=" + str(obj))

    def test_cli_never_accepts_native_parameter_forwarding(self):
        for script in PREPARATION_SCRIPTS:
            with self.subTest(script=script.name):
                result = self.run_script(script.as_posix(), "--", "--output=unexpected")
                self.assertNotEqual(result.returncode, 0)


if __name__ == "__main__":
    unittest.main()

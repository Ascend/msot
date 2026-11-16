import io
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest import mock

from test_environment import SCRIPTS, TIMESTAMP, load_helpers, temporary_directory


class SampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = load_helpers()

    def setUp(self):
        self.temp = temporary_directory("msot tests ")
        self.addCleanup(self.temp.cleanup)
        self.dest = Path(self.temp.name) / "workspace with spaces"
        self.enterContext(mock.patch("sys.stdout", new_callable=io.StringIO))

    def test_interrupted_copy_refuses_even_when_content_matches(self):
        self.helpers.prepare_sample("opgen", self.dest)
        (self.dest / ".msot-pending.json").write_text("interrupted", encoding="utf-8")
        with self.assertRaisesRegex(self.helpers.PreparationError, "Unfinished"):
            self.helpers.prepare_sample("opgen", self.dest)

    def test_copies_both_samples_without_running_them(self):
        for sample, relative in (("mskpp", "mskpp/mskpp_demo.py"), ("opgen", "msopgen/msopgen_demo.json")):
            with self.subTest(sample=sample), mock.patch.object(subprocess, "run") as run, \
                    mock.patch.object(self.helpers, "datetime") as clock, \
                    mock.patch("sys.stdout", new_callable=io.StringIO) as output:
                clock.now.return_value.strftime.return_value = TIMESTAMP
                dest = self.dest / sample
                self.helpers.prepare_sample(sample, dest)
                self.assertEqual((dest / Path(relative).name).read_bytes(),
                                 (self.helpers.EXAMPLES / relative).read_bytes())
                self.assertEqual(output.getvalue(), "{} [INFO] Prepare sample successful, sample path is: {}.\n".format(
                    TIMESTAMP, dest / Path(relative).name))
                clock.now.return_value.strftime.assert_called_once_with("%Y-%m-%d %H:%M:%S")
                run.assert_not_called()

    def test_identical_repeat_does_not_rewrite_file(self):
        self.helpers.prepare_sample("opgen", self.dest)
        file = self.dest / "msopgen_demo.json"
        before = file.stat().st_mtime_ns
        self.helpers.prepare_sample("opgen", self.dest)
        self.assertEqual(file.stat().st_mtime_ns, before)

    def test_conflicting_user_file_is_preserved(self):
        self.dest.mkdir()
        file = self.dest / "mskpp_demo.py"
        file.write_text("user code", encoding="utf-8")
        with self.assertRaisesRegex(self.helpers.PreparationError, "conflict"):
            self.helpers.prepare_sample("mskpp", self.dest)
        self.assertEqual(file.read_text(encoding="utf-8"), "user code")

    def test_directory_instead_of_file_is_not_overwritten(self):
        (self.dest / "mskpp_demo.py").mkdir(parents=True)
        with self.assertRaises(self.helpers.PreparationError):
            self.helpers.prepare_sample("mskpp", self.dest)

    def test_destination_is_a_file(self):
        self.dest.write_text("user", encoding="utf-8")
        with self.assertRaises(self.helpers.PreparationError):
            self.helpers.prepare_sample("mskpp", self.dest)

    def test_symlink_target_is_rejected(self):
        self.dest.mkdir()
        external = Path(self.temp.name) / "external"
        external.write_text("external", encoding="utf-8")
        try:
            (self.dest / "mskpp_demo.py").symlink_to(external)
        except OSError:
            self.skipTest("host does not permit symlinks")
        with self.assertRaises(self.helpers.PreparationError):
            self.helpers.prepare_sample("mskpp", self.dest)
        self.assertEqual(external.read_text(encoding="utf-8"), "external")

    def test_parent_symlink_is_rejected(self):
        external = Path(self.temp.name) / "external"
        external.mkdir()
        try:
            self.dest.symlink_to(external, target_is_directory=True)
        except OSError:
            self.skipTest("host does not permit symlinks")
        with self.assertRaises(self.helpers.PreparationError):
            self.helpers.prepare_sample("mskpp", self.dest / "nested")
        self.assertEqual(list(external.iterdir()), [])

    def test_lock_conflict_and_unrelated_file_preserved(self):
        self.dest.mkdir()
        lock = self.dest / ".msot-prepare.lock"
        lock.write_text("other writer", encoding="utf-8")
        with self.assertRaisesRegex(self.helpers.PreparationError, "lock"):
            self.helpers.prepare_sample("mskpp", self.dest)
        self.assertEqual(lock.read_text(encoding="utf-8"), "other writer")

    def test_dot_dot_path_is_rejected(self):
        with self.assertRaises(self.helpers.PreparationError):
            self.helpers.prepare_sample("mskpp", self.dest / ".." / "other")

    @unittest.skipUnless(shutil.which("bash"), "Bash required")
    def test_real_shell_entry_and_unrelated_working_directory(self):
        result = subprocess.run([shutil.which("bash"), (SCRIPTS / "prepare_sample.sh").as_posix(),
                                 "--sample", "opgen", "--dest", self.dest.as_posix()],
                                cwd=self.temp.name, capture_output=True, text=True, encoding="utf-8", timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.dest / "msopgen_demo.json").is_file())


if __name__ == "__main__":
    unittest.main()

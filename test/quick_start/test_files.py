import os
from pathlib import Path
import stat
import unittest
from unittest import mock

from test_environment import load_helpers, temporary_directory


class FileSafetyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        load_helpers()
        import _files
        cls.files = _files

    def setUp(self):
        self.temp = temporary_directory("msot file safety ")
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)

    def test_failed_multi_file_write_rolls_back_and_cleans_new_files(self):
        first, second = self.directory / "first", self.directory / "second"
        first.write_bytes(b"original")
        original_mode = stat.S_IMODE(first.stat().st_mode)
        write = self.files.atomic_write

        def fail_second(path, data, mode=None):
            if path == second:
                raise OSError("injected disk error")
            return write(path, data, mode)

        pending = self.directory / "state/pending.json"
        with mock.patch.object(self.files, "atomic_write", side_effect=fail_second):
            with self.assertRaisesRegex(self.files.PreparationError, "rolled back"):
                self.files.apply_changes({first: b"changed", second: b"new"}, pending)
        self.assertEqual(first.read_bytes(), b"original")
        self.assertEqual(stat.S_IMODE(first.stat().st_mode), original_mode)
        self.assertFalse(second.exists())
        self.assertFalse(pending.parent.exists())

    def test_failed_rollback_keeps_journal(self):
        first, second = self.directory / "first", self.directory / "second"
        first.write_bytes(b"original")
        write = self.files.atomic_write
        count = 0

        def fail_after_first(path, data, mode=None):
            nonlocal count
            count += 1
            if count >= 3:
                raise OSError("injected persistent failure")
            return write(path, data, mode)

        pending = self.directory / "pending.json"
        with mock.patch.object(self.files, "atomic_write", side_effect=fail_after_first):
            with self.assertRaisesRegex(self.files.PreparationError, "rollback failed"):
                self.files.apply_changes({first: b"changed", second: b"new"}, pending)
        self.assertTrue(pending.exists())

    def test_interruption_keeps_journal(self):
        pending = self.directory / "pending.json"
        write = self.files.atomic_write

        def interrupt(path, data, mode=None):
            if path != pending:
                raise KeyboardInterrupt()
            return write(path, data, mode)

        with mock.patch.object(self.files, "atomic_write", side_effect=interrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.files.apply_changes({self.directory / "target": b"new"}, pending)
        self.assertTrue(pending.exists())

    def test_second_writer_cannot_acquire_same_directory(self):
        with self.files.directory_lock(self.directory):
            with self.assertRaisesRegex(self.files.PreparationError, "lock"):
                with self.files.directory_lock(self.directory):
                    self.fail("second writer entered")
        self.assertFalse((self.directory / ".msot-prepare.lock").exists())

    def test_atomic_write_failure_leaves_original_and_no_temp_files(self):
        target = self.directory / "original"
        target.write_bytes(b"old")
        with mock.patch.object(os, "replace", side_effect=OSError("replace failed")):
            with self.assertRaises(OSError):
                self.files.atomic_write(target, b"new")
        self.assertEqual(target.read_bytes(), b"old")
        self.assertEqual(list(self.directory.glob(".msot-write-*")), [])

    def test_ancestor_symlink_guard_even_on_hosts_without_symlink_privilege(self):
        original = Path.is_symlink
        ancestor = self.directory / "linked"
        with mock.patch.object(Path, "is_symlink", lambda p: p == ancestor or original(p)):
            with self.assertRaisesRegex(self.files.PreparationError, "links"):
                self.files.safe_path(ancestor / "child/file")


if __name__ == "__main__":
    unittest.main()

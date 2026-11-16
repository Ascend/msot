import io
import json
from pathlib import Path
import shutil
import subprocess
import unittest
from unittest import mock

from test_environment import SCRIPTS, load_helpers, temporary_directory
from test_project import KERNEL_CMAKE, make_project


class ModeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = load_helpers()

    def setUp(self):
        self.temp = temporary_directory("msot modes ")
        self.addCleanup(self.temp.cleanup)
        self.project = make_project(Path(self.temp.name) / "work space/AddCustom")
        self.output = self.enterContext(mock.patch("sys.stdout", new_callable=io.StringIO))
        self.helpers.prepare_add_demo(self.project)

    def baseline(self):
        return {p.relative_to(self.project).as_posix(): p.read_bytes()
                for p in self.project.rglob("*") if p.is_file()}

    def prepare(self, mode, fixture=None):
        self.helpers.prepare_mode(self.project, mode, fixture)

    def restore(self):
        self.helpers.restore_demo(self.project)

    def test_all_three_modes_restore_exact_baseline_and_idempotently(self):
        for mode, flags in (("sanitizer", "-sanitizer"), ("debug", "-g -O0"), ("profile", "-g")):
            with self.subTest(mode=mode):
                before = self.baseline()
                self.prepare(mode, "oob" if mode == "sanitizer" else None)
                cmake = (self.project / "op_kernel/CMakeLists.txt").read_bytes()
                self.assertEqual(cmake, ("npu_op_kernel_options(ascendc_kernels ALL OPTIONS {})\n".format(flags)
                                         .encode("utf-8") + KERNEL_CMAKE))
                first = self.baseline()
                self.prepare(mode, "oob" if mode == "sanitizer" else None)
                self.assertEqual(first, self.baseline())
                self.restore()
                self.assertEqual(before, self.baseline())
                self.restore()
                self.assertEqual(before, self.baseline())
        self.assertIn("The deployed build artifacts have not been restored.", self.output.getvalue())

    def test_sanitizer_applies_and_restores_only_selected_fixture(self):
        file = self.project / "op_kernel/add_custom.cpp"
        original = file.read_bytes()
        self.prepare("sanitizer", "oob")
        expected = (self.helpers.EXAMPLES / "mssanitizer/bug_code/add_custom.cpp").read_text(encoding="utf-8").encode("utf-8")
        self.assertEqual(file.read_bytes(), expected)
        self.restore()
        self.assertEqual(file.read_bytes(), original)

    def test_all_mode_messages_have_timestamp_and_info_prefix(self):
        prefix = "2026-11-10 01:35:10 [INFO] "
        for mode, flags in (("sanitizer", "-sanitizer"), ("debug", "-g -O0"), ("profile", "-g")):
            with self.subTest(mode=mode):
                with mock.patch("_project.datetime") as clock, \
                        mock.patch("sys.stdout", new_callable=io.StringIO) as output:
                    clock.now.return_value.strftime.return_value = "2026-11-10 01:35:10"
                    self.prepare(mode, "oob" if mode == "sanitizer" else None)
                messages = ["Successfully prepared {} mode: op_kernel/CMakeLists.txt -> {}".format(mode, flags)]
                if mode == "sanitizer":
                    messages.append("Teaching fixture oob -> op_kernel/add_custom.cpp: DataCopy reads twice the tile length.")
                self.assertEqual(output.getvalue().splitlines(), [prefix + message for message in messages])
                clock.now.assert_called_once_with()
                clock.now.return_value.strftime.assert_called_once_with("%Y-%m-%d %H:%M:%S")
                self.restore()

    def test_restore_messages_have_timestamp_and_info_prefix(self):
        self.prepare("debug")
        with mock.patch("_project.datetime") as clock, \
                mock.patch("sys.stdout", new_callable=io.StringIO) as output:
            clock.now.return_value.strftime.return_value = "2026-11-10 01:35:10"
            self.restore()
        self.assertEqual(output.getvalue(),
                         "2026-11-10 01:35:10 [INFO] Successfully restored source files: "
                         "op_kernel/CMakeLists.txt, op_kernel/add_custom.cpp.\n"
                         "2026-11-10 01:35:10 [INFO] Note: The deployed build artifacts have not been restored. "
                         "To restore them, please re-run the build and deployment process.\n")
        clock.now.assert_called_once_with()
        clock.now.return_value.strftime.assert_called_once_with("%Y-%m-%d %H:%M:%S")

    def test_fixture_is_explicit_and_only_valid_for_sanitizer(self):
        before = self.baseline()
        for mode, fixture in (("sanitizer", None), ("debug", "oob"), ("profile", "oob"), ("unknown", None)):
            with self.subTest(mode=mode, fixture=fixture):
                with self.assertRaises(self.helpers.PreparationError):
                    self.prepare(mode, fixture)
                self.assertEqual(before, self.baseline())

    def test_different_mode_requires_explicit_restore(self):
        self.prepare("debug")
        before = self.baseline()
        with self.assertRaisesRegex(self.helpers.PreparationError, "Restore"):
            self.prepare("profile")
        with self.assertRaisesRegex(self.helpers.PreparationError, "Restore"):
            self.helpers.prepare_add_demo(self.project)
        self.assertEqual(before, self.baseline())

    def test_each_managed_user_edit_blocks_prepare_and_restore(self):
        for name in ("op_host/add_custom.cpp", "op_kernel/add_custom_tiling.h", "op_kernel/add_custom.cpp", "op_kernel/CMakeLists.txt"):
            with self.subTest(name=name):
                file = self.project / name
                original = file.read_bytes()
                file.write_bytes(original + b"\n// user edit\n")
                before = self.baseline()
                with self.assertRaisesRegex(self.helpers.PreparationError, "conflict"):
                    self.prepare("debug")
                with self.assertRaises(self.helpers.PreparationError):
                    self.restore()
                self.assertEqual(before, self.baseline())
                file.write_bytes(original)

    def test_corrupt_or_missing_baseline_prevents_restore(self):
        file = self.project / ".msot-demo/baseline/op_kernel/CMakeLists.txt"
        original = file.read_bytes()
        file.write_bytes(b"corrupt")
        before = self.baseline()
        with self.assertRaises(self.helpers.PreparationError):
            self.restore()
        self.assertEqual(before, self.baseline())
        file.unlink()
        with self.assertRaises(self.helpers.PreparationError):
            self.restore()
        file.write_bytes(original)

    def test_invalid_state_schema_and_traversal_never_write(self):
        file = self.project / ".msot-demo/state.json"
        original = file.read_bytes()
        state = json.loads(original)
        invalid = [[], {}, {**state, "format": True}, {**state, "mode": []},
                   {**state, "soc": "../../external"}, {**state, "baseline": {}},
                   {**state, "current": {"../external": "0" * 64}}]
        for value in invalid:
            with self.subTest(value=value):
                file.write_text(json.dumps(value), encoding="utf-8")
                before = self.baseline()
                with self.assertRaises(self.helpers.PreparationError):
                    self.restore()
                self.assertEqual(before, self.baseline())
        file.write_bytes(b"not JSON")
        with self.assertRaises(self.helpers.PreparationError):
            self.restore()
        file.write_bytes(original)

    def test_invalid_soc_state_is_rejected_without_writing_files(self):
        path = self.project / ".msot-demo/state.json"
        original = path.read_bytes()
        state = json.loads(original)
        for soc in ("ascend", "ascend_910", "ascend-910", "ascend910/../x", "ascend910b;echo unsafe"):
            with self.subTest(soc=soc):
                path.write_text(json.dumps({**state, "soc": soc}), encoding="utf-8")
                before = self.baseline()
                for action in (lambda: self.prepare("debug"), self.restore):
                    with self.assertRaisesRegex(self.helpers.PreparationError, "state schema"):
                        action()
                    self.assertEqual(self.baseline(), before)
        path.write_bytes(original)

    def test_unfinished_transaction_blocks_all_project_actions(self):
        (self.project / ".msot-demo/pending.json").write_text("interrupted", encoding="utf-8")
        before = self.baseline()
        for action in (lambda: self.prepare("debug"), self.restore,
                       lambda: self.helpers.prepare_add_demo(self.project)):
            with self.assertRaisesRegex(self.helpers.PreparationError, "Unfinished"):
                action()
            self.assertEqual(before, self.baseline())

    def test_lock_blocks_restore_and_prepare(self):
        lock = self.project / ".msot-prepare.lock"
        lock.write_text("another operation", encoding="utf-8")
        for action in (lambda: self.prepare("debug"), self.restore):
            with self.assertRaisesRegex(self.helpers.PreparationError, "lock"):
                action()
        self.assertEqual(lock.read_text(encoding="utf-8"), "another operation")

    def test_mode_write_failure_rolls_back_and_can_retry(self):
        import _files
        before = self.baseline()
        write = _files.atomic_write
        count = 0

        def fail_once(path, data, mode=None):
            nonlocal count
            count += 1
            if count == 3:
                raise OSError("injected write failure")
            return write(path, data, mode)

        with mock.patch.object(_files, "atomic_write", side_effect=fail_once):
            with self.assertRaisesRegex(self.helpers.PreparationError, "rolled back"):
                self.prepare("sanitizer", "oob")
        self.assertEqual(before, self.baseline())
        self.prepare("sanitizer", "oob")
        self.restore()
        self.assertEqual(before, self.baseline())

    def test_unmanaged_project_cannot_be_switched_or_restored(self):
        fresh = make_project(Path(self.temp.name) / "fresh/AddCustom")
        for action in (lambda: self.helpers.prepare_mode(fresh, "debug"),
                       lambda: self.helpers.restore_demo(fresh)):
            with self.assertRaisesRegex(self.helpers.PreparationError, "state"):
                action()
        self.assertFalse((fresh / ".msot-demo").exists())

    @unittest.skipUnless(shutil.which("bash"), "Bash required")
    def test_real_shell_mode_and_restore(self):
        for script, args in (("prepare_mode.sh", ["--mode", "debug"]), ("restore_demo.sh", [])):
            result = subprocess.run([shutil.which("bash"), (SCRIPTS / script).as_posix(),
                                     "--project", self.project.as_posix(), *args],
                                    capture_output=True, text=True, encoding="utf-8", timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()

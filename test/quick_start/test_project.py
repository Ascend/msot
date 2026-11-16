import io
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier
import unittest
from unittest import mock

from test_environment import SCRIPTS, TIMESTAMP, load_helpers, temporary_directory


GENERATED = {
    "op_host/add_custom.cpp": "add_custom.cpp.in",
    "op_kernel/add_custom.cpp": "kernel.cpp.in",
    "op_kernel/add_custom_tiling.h": "add_custom_tiling.h.in",
}
KERNEL_CMAKE = b"# CANN teaching build scaffold\nnpu_op_kernel_sources(ascendc_kernels KERNEL_DIR ./)\n"


def make_project(project, soc="ascend910b"):
    for relative, template in GENERATED.items():
        target = project / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text((SCRIPTS / "templates" / template).read_text(encoding="utf-8")
                          .replace("__SOC__", soc), encoding="utf-8", newline="\n")
    (project / "op_kernel/CMakeLists.txt").write_bytes(KERNEL_CMAKE)
    (project / "CMakeLists.txt").write_text("# CANN project\n", encoding="utf-8")
    (project / "op_host/CMakeLists.txt").write_text("# CANN host\n", encoding="utf-8")
    (project / "CMakePresets.json").write_text("{}\n", encoding="utf-8")
    (project / "build.sh").write_text("#!/bin/bash\nexit 99\n", encoding="utf-8")
    return project


class ProjectTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.helpers = load_helpers()

    def setUp(self):
        self.temp = temporary_directory("msot project ")
        self.addCleanup(self.temp.cleanup)
        self.project = make_project(Path(self.temp.name) / "work space" / "AddCustom")
        self.output = self.enterContext(mock.patch("sys.stdout", new_callable=io.StringIO))

    def snapshot(self):
        return {p.relative_to(self.project).as_posix(): p.read_bytes()
                for p in self.project.rglob("*") if p.is_file()}

    def prepare(self):
        self.helpers.prepare_add_demo(self.project)

    def test_preserves_generated_soc_and_copies_all_assets(self):
        host = self.project / "op_host/add_custom.cpp"
        host.write_text(host.read_text(encoding="utf-8").replace("ascend910b", "ascend310p"), encoding="utf-8")
        with mock.patch("_project.datetime") as clock:
            clock.now.return_value.strftime.return_value = TIMESTAMP
            self.prepare()
        clock.now.assert_called_once_with()
        clock.now.return_value.strftime.assert_called_once_with("%Y-%m-%d %H:%M:%S")
        self.assertIn('.AddConfig("ascend310p")', host.read_text(encoding="utf-8"))
        self.assertNotIn("user kernel impl", (self.project / "op_kernel/add_custom.cpp").read_text(encoding="utf-8"))
        self.assertTrue((self.project.parent / "caller/run.sh").is_file())
        self.assertFalse((self.project / "build_out").exists())
        self.assertFalse((self.project.parent / "caller/build").exists())
        self.assertEqual(json.loads((self.project / ".msot-demo/state.json").read_text(encoding="utf-8"))["mode"], "normal")
        self.assertEqual(self.output.getvalue(),
                         "{0} [INFO] Teaching implementation prepared; preserved SoC: ascend310p\n"
                         "{0} [INFO] Prepare sample script successful.\n"
                         "{0} [INFO] The project path is: {1}\n"
                         "{0} [INFO] The caller path is: {2}\n".format(
                             TIMESTAMP, self.project, self.project.parent / "caller"))

    def test_idempotent_assembly_and_immutable_baseline(self):
        self.prepare()
        before = self.snapshot()
        self.prepare()
        self.assertEqual(before, self.snapshot())

    def test_soc_separators_are_preserved_through_repeats_modes_and_restoration(self):
        for index, soc in enumerate(("ascend910_9391", "ascend910b4-1")):
            with self.subTest(soc=soc):
                project = make_project(Path(self.temp.name) / ("soc-" + str(index)) / "AddCustom", soc)
                self.helpers.prepare_add_demo(project)
                baseline = {p.relative_to(project).as_posix(): p.read_bytes()
                            for p in project.rglob("*") if p.is_file()}
                self.assertIn('.AddConfig("{}")'.format(soc),
                              (project / "op_host/add_custom.cpp").read_text(encoding="utf-8"))
                self.assertEqual(json.loads((project / ".msot-demo/state.json").read_bytes())["soc"], soc)
                self.helpers.prepare_add_demo(project)
                for mode in ("sanitizer", "debug", "profile"):
                    with self.subTest(mode=mode):
                        fixture = "oob" if mode == "sanitizer" else None
                        self.helpers.prepare_mode(project, mode, fixture)
                        self.helpers.prepare_mode(project, mode, fixture)
                        state = json.loads((project / ".msot-demo/state.json").read_bytes())
                        self.assertEqual(state["soc"], soc)
                        self.assertEqual(state["mode"], mode)
                        self.helpers.restore_demo(project)
                        self.helpers.restore_demo(project)
                        current = {p.relative_to(project).as_posix(): p.read_bytes()
                                   for p in project.rglob("*") if p.is_file()}
                        self.assertEqual(current, baseline)
                self.assertFalse((project / "build_out").exists())
                self.assertFalse((project.parent / "caller/build").exists())

    def test_invalid_generated_soc_is_rejected_without_writing_files(self):
        invalid = ("ascend", "ascend_910", "ascend-910", "ascend910/../x", "ascend910 b",
                   "ascend910b;echo unsafe", "ascend910b\\x", 'ascend910b"')
        for index, soc in enumerate(invalid):
            with self.subTest(soc=soc):
                project = make_project(Path(self.temp.name) / ("invalid-" + str(index)) / "AddCustom", soc)
                before = {p.relative_to(project).as_posix(): p.read_bytes()
                          for p in project.rglob("*") if p.is_file()}
                with self.assertRaisesRegex(self.helpers.PreparationError, "Expected exactly one"):
                    self.helpers.prepare_add_demo(project)
                after = {p.relative_to(project).as_posix(): p.read_bytes()
                         for p in project.rglob("*") if p.is_file()}
                self.assertEqual(after, before)
                self.assertFalse((project / ".msot-demo").exists())
                self.assertFalse((project.parent / "caller").exists())

    def test_rejects_each_edited_generated_source_without_partial_writes(self):
        for relative in GENERATED:
            with self.subTest(relative=relative):
                project = make_project(Path(self.temp.name) / relative.replace("/", "_") / "AddCustom")
                file = project / relative
                file.write_bytes(file.read_bytes() + b"\n// user's edit\n")
                before = {p: p.read_bytes() for p in project.rglob("*") if p.is_file()}
                with self.assertRaisesRegex(self.helpers.PreparationError, "template|conflict"):
                    self.helpers.prepare_add_demo(project)
                self.assertTrue(all(p.read_bytes() == data for p, data in before.items()))
                self.assertFalse((project / ".msot-demo").exists())

    def test_duplicate_or_missing_soc_rejected(self):
        host = self.project / "op_host/add_custom.cpp"
        generated = host.read_bytes()
        for soc in (b"ascend910b", b"ascend910_9391", b"ascend910b4-1"):
            original = generated.replace(b"ascend910b", soc)
            for data in (original.replace(b"AddConfig", b"OtherConfig"),
                         original + b'\nother.AddConfig("ascend950");'):
                with self.subTest(soc=soc, data=data):
                    host.write_bytes(data)
                    with self.assertRaises(self.helpers.PreparationError):
                        self.prepare()

    def test_caller_conflict_does_not_modify_project(self):
        caller = self.project.parent / "caller"
        caller.mkdir()
        (caller / "main.cpp").write_text("user code", encoding="utf-8")
        before = self.snapshot()
        with self.assertRaisesRegex(self.helpers.PreparationError, "conflict"):
            self.prepare()
        self.assertEqual(before, self.snapshot())
        self.assertEqual((caller / "main.cpp").read_text(encoding="utf-8"), "user code")

    def test_two_projects_do_not_share_soc_or_state(self):
        other = make_project(Path(self.temp.name) / "other" / "AddCustom", "ascend950")
        self.prepare()
        self.helpers.prepare_add_demo(other)
        self.assertIn('"ascend910b"', (self.project / "op_host/add_custom.cpp").read_text(encoding="utf-8"))
        self.assertIn('"ascend950"', (other / "op_host/add_custom.cpp").read_text(encoding="utf-8"))

    def test_two_projects_can_be_prepared_concurrently(self):
        other = make_project(Path(self.temp.name) / "parallel/AddCustom", "ascend950")
        barrier = Barrier(2)

        def prepare(project):
            barrier.wait(timeout=15)
            self.helpers.prepare_add_demo(project)

        with ThreadPoolExecutor(max_workers=2) as pool:
            list(pool.map(prepare, (self.project, other)))
        for project, soc in ((self.project, "ascend910b"), (other, "ascend950")):
            state = json.loads((project / ".msot-demo/state.json").read_text(encoding="utf-8"))
            self.assertEqual(state["soc"], soc)
            self.assertIn('"' + soc + '"', (project / "op_host/add_custom.cpp").read_text(encoding="utf-8"))

    def test_existing_unmanaged_identical_demo_can_be_adopted(self):
        self.prepare()
        state = self.project / ".msot-demo"
        for file in sorted(state.rglob("*"), key=lambda p: len(p.parts), reverse=True):
            file.unlink() if file.is_file() else file.rmdir()
        state.rmdir()
        self.prepare()
        self.assertTrue((state / "state.json").exists())

    def test_legacy_backup_and_mode_edits_are_rejected(self):
        cmake = self.project / "op_kernel/CMakeLists.txt"
        legacy = cmake.with_suffix(".txt.bak")
        legacy.write_bytes(KERNEL_CMAKE)
        with self.assertRaisesRegex(self.helpers.PreparationError, "legacy|bak"):
            self.prepare()
        legacy.unlink()
        cmake.write_bytes(b"npu_op_kernel_options(ascendc_kernels ALL OPTIONS -g)\n" + KERNEL_CMAKE)
        with self.assertRaises(self.helpers.PreparationError):
            self.prepare()

    def test_empty_or_interrupted_state_is_not_adopted(self):
        (self.project / ".msot-demo").mkdir()
        with self.assertRaisesRegex(self.helpers.PreparationError, "state"):
            self.prepare()

    def test_unrelated_caller_files_survive(self):
        caller = self.project.parent / "caller/build"
        caller.mkdir(parents=True)
        (caller / "user-output").write_text("keep", encoding="utf-8")
        self.prepare()
        self.assertEqual((caller / "user-output").read_text(encoding="utf-8"), "keep")

    def test_late_caller_write_failure_rolls_back_project_and_state(self):
        import _files
        before = self.snapshot()
        write = _files.atomic_write
        failed = False

        def fail_once(path, data, mode=None):
            nonlocal failed
            if path == self.project.parent / "caller/main.cpp" and not failed:
                failed = True
                raise OSError("injected caller write failure")
            return write(path, data, mode)

        with mock.patch.object(_files, "atomic_write", side_effect=fail_once):
            with self.assertRaisesRegex(self.helpers.PreparationError, "rolled back"):
                self.prepare()
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.project / ".msot-demo").exists())
        self.prepare()

    def test_default_conditional_debug_cmake_is_preserved_as_baseline(self):
        cmake = (b'if ("${CMAKE_BUILD_TYPE}x" STREQUAL "Debugx")\n'
                 b'    add_ops_compile_options(ALL OPTIONS -g -O0 --cce-ignore-always-inline=true)\n'
                 b'endif()\n' + KERNEL_CMAKE)
        (self.project / "op_kernel/CMakeLists.txt").write_bytes(cmake)
        self.prepare()
        self.assertEqual((self.project / ".msot-demo/baseline/op_kernel/CMakeLists.txt").read_bytes(), cmake)

    def test_cann_9_0_0_cmake_is_preserved_through_all_modes(self):
        # Snapshot from an unedited CANN 9.0.0 msopgen AddCustom project.
        cmake = (Path(__file__).parent / "fixtures/cann_9_0_0_kernel.CMakeLists.txt").read_bytes()
        target = self.project / "op_kernel/CMakeLists.txt"
        target.write_bytes(cmake)
        self.prepare()
        self.assertEqual(target.read_bytes(), cmake)
        self.prepare()
        self.assertEqual(target.read_bytes(), cmake)
        baseline = self.snapshot()
        for mode, flags in (("sanitizer", "-sanitizer"), ("debug", "-g -O0"), ("profile", "-g")):
            with self.subTest(mode=mode):
                fixture = "oob" if mode == "sanitizer" else None
                self.helpers.prepare_mode(self.project, mode, fixture)
                expected = ("npu_op_kernel_options(ascendc_kernels ALL OPTIONS {})\n".format(flags)
                            .encode("utf-8") + cmake)
                self.assertEqual(target.read_bytes(), expected)
                self.helpers.prepare_mode(self.project, mode, fixture)
                self.assertEqual(target.read_bytes(), expected)
                self.assertEqual((self.project / ".msot-demo/baseline/op_kernel/CMakeLists.txt").read_bytes(), cmake)
                self.helpers.restore_demo(self.project)
                self.assertEqual(self.snapshot(), baseline)

    def test_cann_9_0_0_default_does_not_hide_manual_flags(self):
        cmake = (Path(__file__).parent / "fixtures/cann_9_0_0_kernel.CMakeLists.txt").read_bytes()
        target = self.project / "op_kernel/CMakeLists.txt"
        for flags in ("-g", "-O0", "-sanitizer"):
            option = "npu_op_kernel_options(ascendc_kernels ALL OPTIONS {})\n".format(flags).encode("utf-8")
            for content in (option + cmake, cmake + option):
                with self.subTest(flags=flags, prepended=content.startswith(option)):
                    target.write_bytes(content)
                    before = self.snapshot()
                    with self.assertRaisesRegex(self.helpers.PreparationError, "flags"):
                        self.prepare()
                    self.assertEqual(self.snapshot(), before)
                    self.assertFalse((self.project / ".msot-demo").exists())

    def test_cann_9_0_0_crlf_cmake_is_preserved(self):
        cmake = (Path(__file__).parent / "fixtures/cann_9_0_0_kernel.CMakeLists.txt").read_text(encoding="utf-8")
        content = cmake.replace("\n", "\r\n").encode("utf-8")
        target = self.project / "op_kernel/CMakeLists.txt"
        target.write_bytes(content)
        self.prepare()
        self.helpers.prepare_mode(self.project, "profile")
        self.helpers.restore_demo(self.project)
        self.assertEqual(target.read_bytes(), content)
        self.assertEqual((self.project / ".msot-demo/baseline/op_kernel/CMakeLists.txt").read_bytes(), content)

    def test_unreviewed_conditional_debug_blocks_are_rejected(self):
        cmake = (Path(__file__).parent / "fixtures/cann_9_0_0_kernel.CMakeLists.txt").read_bytes()
        for content in (cmake.replace(b"Debugx", b"Releasex"),
                        cmake.replace(b"ALL OPTIONS -g -O0", b"ALL OPTIONS -g -O0 -sanitizer"),
                        cmake.replace(b"npu_op_kernel_options(ascendc_kernels", b"npu_op_kernel_options(other_kernels")):
            with self.subTest(content=content):
                (self.project / "op_kernel/CMakeLists.txt").write_bytes(content)
                before = self.snapshot()
                with self.assertRaisesRegex(self.helpers.PreparationError, "flags"):
                    self.prepare()
                self.assertEqual(self.snapshot(), before)

    def test_quoted_and_semicolon_separated_manual_flags_are_rejected(self):
        cmake = self.project / "op_kernel/CMakeLists.txt"
        for option in (b'set(CMAKE_CXX_FLAGS "-O0")\n',
                       b'set(FLAGS "-g;-O0")\n',
                       b'add_ops_compile_options(ALL OPTIONS "-sanitizer")\n'):
            with self.subTest(option=option):
                cmake.write_bytes(KERNEL_CMAKE + option)
                before = self.snapshot()
                with self.assertRaisesRegex(self.helpers.PreparationError, "flags"):
                    self.prepare()
                self.assertEqual(before, self.snapshot())


if __name__ == "__main__":
    unittest.main()

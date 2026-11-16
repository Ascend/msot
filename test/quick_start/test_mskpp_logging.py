"""Sample logging tests that do not require msKPP or device execution."""
import importlib.util
import io
import logging
from pathlib import Path
import runpy
import sys
import types
import unittest
from unittest import mock

from test_environment import ROOT, temporary_directory


class MskppLoggingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        stub = types.ModuleType("mskpp")
        stub.vadd = stub.Tensor = stub.Chip = mock.Mock()
        spec = importlib.util.spec_from_file_location(
            "mskpp_demo_logging", ROOT / "example/quick_start/mskpp/mskpp_demo.py")
        cls.sample = importlib.util.module_from_spec(spec)
        with mock.patch.dict(sys.modules, {"mskpp": stub}):
            spec.loader.exec_module(cls.sample)

    def test_formatter_removes_only_leading_message_whitespace(self):
        formatter = self.sample.ConsoleLogFormatter(
            "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S")
        for level in (logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR):
            with self.subTest(level=level):
                record = logging.LogRecord("mskpp", level, __file__, 1, "   MOV %s", ("GM  TO UB",), None)
                line = formatter.format(record)
                self.assertRegex(line, r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} \[" +
                                 logging.getLevelName(level) + r"\] MOV GM  TO UB$")
                self.assertEqual(record.msg, "   MOV %s")
                self.assertEqual(record.args, ("GM  TO UB",))

    def test_console_configuration_preserves_file_logging_and_level(self):
        with temporary_directory("msot-mskpp-logging-") as directory:
            logger = logging.Logger("mskpp-sample-test", logging.INFO)
            output = io.StringIO()
            console = logging.StreamHandler(output)
            logfile = Path(directory) / "sample.log"
            file_handler = logging.FileHandler(logfile)
            original_formatter = logging.Formatter("FILE: %(message)s")
            file_handler.setFormatter(original_formatter)
            logger.addHandler(console)
            logger.addHandler(file_handler)
            try:
                with mock.patch.object(self.sample.logging, "getLogger", return_value=logger):
                    self.sample.configure_console_logging()
                logger.info("   Metrics:")
                self.assertEqual(logger.level, logging.INFO)
                self.assertIs(file_handler.formatter, original_formatter)
                self.assertRegex(output.getvalue(), r"\[INFO\] Metrics:\n$")
                self.assertEqual(logfile.read_text(), "FILE:    Metrics:\n")
            finally:
                file_handler.close()
                console.close()

    def run_sample(self, chip):
        stub = types.ModuleType("mskpp")
        stub.Chip = mock.Mock(return_value=chip)
        stub.Tensor = mock.MagicMock()
        stub.vadd = mock.MagicMock()
        with mock.patch.dict(sys.modules, {"mskpp": stub}), \
                mock.patch.object(logging, "getLogger", return_value=logging.Logger("mskpp-main-test")):
            runpy.run_path(str(ROOT / "example/quick_start/mskpp/mskpp_demo.py"), run_name="__main__")

    def test_success_message_uses_actual_output_directory_after_modeling(self):
        chip = mock.MagicMock()
        chip.__enter__.return_value = chip
        chip.output_dir = "/workspace/MSKPP20261110131410"
        events = []
        chip.__exit__.side_effect = lambda *args: events.append("modeling finished") or False
        with mock.patch.object(logging, "info", side_effect=lambda *args: events.append("success")) as info:
            self.run_sample(chip)
        self.assertEqual(events, ["modeling finished", "success"])
        info.assert_called_once_with("MSKPP modeling completed successfully, result path is: %s.", chip.output_dir)

    def test_no_success_message_when_modeling_fails(self):
        chip = mock.MagicMock()
        chip.__enter__.return_value = chip
        chip.__exit__.side_effect = RuntimeError("modeling failed")
        with mock.patch.object(logging, "info") as info:
            with self.assertRaisesRegex(RuntimeError, "modeling failed"):
                self.run_sample(chip)
        info.assert_not_called()


if __name__ == "__main__":
    unittest.main()

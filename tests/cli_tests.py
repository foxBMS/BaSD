import argparse
import logging
import sys
import unittest
from pathlib import Path

from click.testing import CliRunner

ROOT = Path(__file__).parent.parent
sys.path.append(str((ROOT / "src").resolve()))

from basd import main  # pylint: disable=wrong-import-position

TEST_CELL_DIR = ROOT / "tests/cells"
TEST_CELL_EXAMPLE_CELL = ROOT / "tests/cells/Example_Cell.json"
TEST_CELL_DUMMY_CELL = ROOT / "tests/cells/Dummy_Cell.json"


def make_test_cmd(cmd_args, cli=main) -> tuple:
    """Adds logging to the command"""
    logging.debug("\n\tcmd: %s\n\targs: %s", cli, cmd_args)
    return cli, cmd_args


class TestMainCommandsHelp(unittest.TestCase):
    """Testing the main command its subcommands help to ensure that it basically works"""

    def test_basd_main_help_no_args(self):
        """Check the BaSD main help works"""
        runner = CliRunner()
        result = runner.invoke(*make_test_cmd([]))
        self.assertEqual(result.exit_code, 0)

    def test_basd_main_help(self):
        """Check the BaSD main help works"""
        runner = CliRunner()
        result = runner.invoke(*make_test_cmd(["--help"]))
        self.assertEqual(result.exit_code, 0)

    def test_basd_cad_main_help(self):
        """Check the BaSD main cad help works"""
        runner = CliRunner()
        result = runner.invoke(*make_test_cmd(["cad", "--help"]))
        self.assertEqual(result.exit_code, 0)

    def test_basd_db_main_help(self):
        """Check the BaSD main db help works"""
        runner = CliRunner()
        result = runner.invoke(*make_test_cmd(["db", "--help"]))
        self.assertEqual(result.exit_code, 0)

    def test_basd_design_main_help(self):
        """Check the BaSD main design help works"""
        runner = CliRunner()
        result = runner.invoke(*make_test_cmd(["design", "--help"]))
        self.assertEqual(result.exit_code, 0)

    def test_basd_sim_main_help(self):
        """Check the BaSD main sim help works"""
        runner = CliRunner()
        result = runner.invoke(*make_test_cmd(["sim", "--help"]))
        self.assertEqual(result.exit_code, 0)


class TestMainOptions(unittest.TestCase):
    """Tests options of the main command"""

    def test_basd_main_s_option(self):
        """Checks that the configuration is returned"""
        runner = CliRunner()
        result = runner.invoke(*make_test_cmd(["--show-config"]))
        self.assertEqual(result.exit_code, 0)

    def test_basd_main_version_option(self):
        """Checks that the configuration is returned"""
        runner = CliRunner()
        result = runner.invoke(*make_test_cmd(["--version"]))
        self.assertEqual(result.exit_code, 0)


class TestDb(unittest.TestCase):
    """Tests the database functionalities"""

    def setUp(self) -> None:
        """Start from a cleaned database at every test step"""
        runner = CliRunner()
        runner.invoke(*make_test_cmd(["db", "rm", "--all-cells"]))
        return super().setUp()

    def test_basd_db_rm(self):
        """Checks removing the database works"""
        runner = CliRunner()
        result = runner.invoke(*make_test_cmd(["db", "rm", "--all-cells"]))
        self.assertEqual(result.exit_code, 0)

    def test_basd_db_rm_specific_cell(self):
        """Checks removing a cell from the database works"""
        runner = CliRunner()
        result = runner.invoke(*make_test_cmd(["db", "add", str(TEST_CELL_DIR)]))
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(*make_test_cmd(["db", "list"]))
        cells_before = sorted(result.output.splitlines())
        result = runner.invoke(*make_test_cmd(["db", "rm", "dummy:cell"]))
        self.assertEqual(result.exit_code, 0)
        result = runner.invoke(*make_test_cmd(["db", "list"]))
        self.assertEqual(result.exit_code, 0)
        cells_after = sorted(result.output.splitlines())
        self.assertEqual(cells_before, sorted(cells_after + ["dummy:cell"]))

    def test_basd_db_add_cells_from_directory(self):
        """Checks adding cells to database works"""
        runner = CliRunner()
        runner.invoke(*make_test_cmd(["db", "add", str(TEST_CELL_DIR)]))
        test_cells = sorted([i.name for i in TEST_CELL_DIR.rglob("**/*.json")])
        result = runner.invoke(*make_test_cmd(["--show-config"]))
        db_path = None
        for i in result.output.splitlines():
            if "database directory" in i:
                db_path = Path(i.split(":", maxsplit=1)[1].strip())
                break
        if not db_path:
            self.fail("Could not find database path")
        installed_cells = sorted([i.name for i in db_path.glob("*.json")])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(test_cells, installed_cells)

    def test_basd_db_add_cells_from_file(self):
        """Checks adding cells to database works"""
        runner = CliRunner()
        runner.invoke(*make_test_cmd(["db", "add", str(TEST_CELL_DUMMY_CELL)]))
        result = runner.invoke(*make_test_cmd(["--show-config"]))
        db_path = None
        for i in result.output.splitlines():
            if "database directory" in i:
                db_path = Path(i.split(":", maxsplit=1)[1].strip())
                break
        if not db_path:
            self.fail("Could not find database path")
        installed_cells = sorted([i.name for i in db_path.glob("*.json")])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual([TEST_CELL_DUMMY_CELL.name], installed_cells)

    def test_basd_db_add_cells_from_files(self):
        """Checks adding cells to database works"""
        runner = CliRunner()
        runner.invoke(
            *make_test_cmd(
                ["db", "add", str(TEST_CELL_DUMMY_CELL), str(TEST_CELL_EXAMPLE_CELL)]
            )
        )
        result = runner.invoke(*make_test_cmd(["--show-config"]))
        db_path = None
        for i in result.output.splitlines():
            if "database directory" in i:
                db_path = Path(i.split(":", maxsplit=1)[1].strip())
                break
        if not db_path:
            self.fail("Could not find database path")
        installed_cells = sorted([i.name for i in db_path.glob("*.json")])
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(
            [TEST_CELL_DUMMY_CELL.name, TEST_CELL_EXAMPLE_CELL.name], installed_cells
        )

    def test_basd_db_list(self):
        """Checks listing cells that are in the database"""
        runner = CliRunner()
        runner.invoke(*make_test_cmd(["db", "add", str(TEST_CELL_DUMMY_CELL)]))

        result = runner.invoke(*make_test_cmd(["db", "list"]))
        cells = result.output.splitlines()
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(cells, ["dummy:cell"])

    def test_basd_db_list_empty(self):
        """Checks listing on an empty database works"""
        runner = CliRunner()
        result = runner.invoke(*make_test_cmd(["db", "list"]))
        self.assertEqual(result.exit_code, 1)
        self.assertEqual("Cell database is empty", result.output.strip())

    def test_basd_db_show(self):
        """Checks showing cells details works"""
        runner = CliRunner()
        runner.invoke(*make_test_cmd(["db", "add", str(TEST_CELL_DUMMY_CELL)]))

        result = runner.invoke(*make_test_cmd(["db", "show", "dummy:cell"]))
        show = result.output.splitlines()
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(show[0], "Cell: dummy:cell")
        self.assertEqual(
            show[1],
            "Identification(manufacturer='dummy', model='cell', manufacturer_safe='dummy', model_safe='cell')",
        )
        self.assertEqual(
            show[2],
            "Mechanics(weight=0.068, format='cylindrical', standard=False, height=0.07, length=0.021, width=0.021, volume=9.693180000000001e-05)",
        )
        self.assertEqual(
            show[3],
            "Electrics(capacity=CapacitySpec(initial=7.5), cont_current=ContinuousCurrentSpec(charge=18.0, discharge=18.0), energy=EnergySpec(nominal=18.0, minimum=18.0), voltage=VoltageSpec(nominal=3.65, minimum=2.9, maximum=4.25), discharge_curve=[4.25, 4.0, 3.8, 3.65, 3.5, 3.3, 3.1, 2.9])",
        )

    def test_basd_db_show_invalid_cell(self):
        """Checks showing a invalid cell creates an error"""
        runner = CliRunner()
        runner.invoke(*make_test_cmd(["db", "add", str(TEST_CELL_DUMMY_CELL)]))

        result = runner.invoke(*make_test_cmd(["db", "show", "bla:blu"]))
        self.assertEqual(result.exit_code, 1)
        self.assertEqual("cell 'bla:blu' not found", result.output.strip())

        result = runner.invoke(*make_test_cmd(["db", "show", "bla:blu", "foo:bar"]))
        self.assertEqual(result.exit_code, 2)
        self.assertEqual(
            "cell 'bla:blu' not found", result.output.splitlines()[0].strip()
        )
        self.assertEqual(
            "cell 'foo:bar' not found", result.output.splitlines()[1].strip()
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="BaSD unit test runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-v",
        "--verbose",
        dest="verbosity",
        action="count",
        default=0,
        help="Sets the test verbosity",
    )
    args = parser.parse_args()
    logging_levels = {
        0: logging.CRITICAL,
        1: logging.ERROR,
        2: logging.WARNING,
        3: logging.INFO,
        4: logging.DEBUG,
    }
    logging.basicConfig(
        level=logging_levels[min(args.verbosity, max(logging_levels.keys()))]
    )
    unittest.main()

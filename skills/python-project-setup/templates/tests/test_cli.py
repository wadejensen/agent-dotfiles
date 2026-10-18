from click.testing import CliRunner

from PACKAGE_NAME.cli import main


def test_main_runs_ok() -> None:
    result = CliRunner().invoke(main, [])
    assert result.exit_code == 0


def test_main_verbose_runs_ok() -> None:
    result = CliRunner().invoke(main, ["--verbose"])
    assert result.exit_code == 0

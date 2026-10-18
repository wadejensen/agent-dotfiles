import logging

import click

logger = logging.getLogger("PACKAGE_NAME")


@click.command()
@click.option("--verbose", is_flag=True, help="Enable debug logging.")
def main(verbose: bool) -> None:
    """PROJECT_NAME command-line interface."""
    logging.basicConfig(level=logging.DEBUG if verbose else logging.INFO)
    logger.info("hello from PACKAGE_NAME")


if __name__ == "__main__":
    main()

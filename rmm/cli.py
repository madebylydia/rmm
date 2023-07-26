import pathlib
import ccl
import click


cli = click.Group("RMM: reMarkable Manga")
ccl.register_commands(cli, pathlib.Path(__file__, "..", "commands"))


def main():
    cli.main()

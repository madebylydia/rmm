import sys
from typing import Any

import click
from aspreno import ArgumentedException


class UnacceptableResponse(ArgumentedException):
    """
    An exception raised when an API response cannot be processed.

    Parameters
    ----------
    ArgumentedException : _type_
        _description_
    """

    def handle(self, data: dict[Any, Any], **kwargs: Any):
        click.echo("Unacceptable response from API.")
        click.echo(data)
        sys.exit(1)

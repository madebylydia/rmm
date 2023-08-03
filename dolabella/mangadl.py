import sys
from typing import NewType

import click

from dolabella.exceptions.unacceptable_response import UnacceptableResponse
from dolabella.maestro import Maestro
from dolabella.models import Manga
from dolabella.requester import search_mangas
from dolabella.utils import get_or_first
from dolabella.types import Collection

VolSelection = NewType("VolSelection", str)

CMDS_HELP = (
    "Help\n\n"
    'In order to interact with commands, you should "lock" a manga, this mean select a '
    "manga to then download it, get its information, etc."
    '\nTo lock a manga, simply put a number. To release lock, put "0".'
    "into the command input."
    "\n\nCommands"
    "\n\n\td (Download)"
    "\n\tDownload a manga. Require lock."
    "\n\n\ti (Info)"
    "\n\tGet more information about a manga. Require lock."
    "\n\n\tv (Volume)"
    "\n\tSelect a range of volume to download. Require lock."
    "\n\n\ta (Aggregate)"
    "\n\tGet info about a manga's volumes & chapters."
)


@click.command()
@click.argument("name", type=click.STRING)
def newmangadl(name: str):
    click.echo("Registering Aspreno...")
    # register_global_handler(ExceptionHandler())

    click.echo(f"Searching for {name}...")
    data = search_mangas(name)

    if data["result"] != "ok":
        raise UnacceptableResponse(**{"data": data})

    if len(data["result"]) <= 0:
        click.echo("No results found.")
        sys.exit(0)

    collection = Collection(
        {
            index: Manga(
                manga["id"],
                get_or_first(manga["attributes"]["title"], "en"),
                get_or_first(manga["attributes"]["description"], "en"),
                manga["attributes"]["year"],
                manga["attributes"]["status"],
                manga["attributes"]["contentRating"],
                manga["attributes"]["availableTranslatedLanguages"],
            )
            for index, manga in enumerate(data["data"], start=1)
        }
    )

    click.echo(f"Found {len(collection)} mangas.")

    maestro = Maestro(collection)

    click.echo(maestro.list_manga(collection))
    while not maestro.can_exit:
        output = maestro.display_command_output()
        user_input = click.prompt(output, prompt_suffix="")

        maestro.process(user_input)

    click.echo("Many thanks for using Dolabella!")

import sys
import typing

import click
from dolabella.downloader import download

from dolabella.types import Collection, LockList

if typing.TYPE_CHECKING:
    from dolabella.models import Manga


HELP = (
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


class Maestro:
    """
    Maestro is the class that contain the command within "mangadl", such as "lock", "download",
    etc. Basically the core of the app.
    """

    collection: Collection
    locked: int | None
    volume_range: LockList | None
    can_exit: bool

    def __init__(self, collection: Collection) -> None:
        self.collection = collection
        self.locked = None
        self.volume_range = None
        self.can_exit = False

    @staticmethod
    def help() -> None:
        click.echo(HELP)

    @staticmethod
    def user_range_to_list_range(input: str) -> LockList | None:
        try:
            result = LockList([])
            for part in input.split(","):
                if "-" in part:
                    a, b = part.split("-")
                    a, b = int(a), int(b)
                    result.extend([str(i) for i in range(a, b + 1)])
                else:
                    result.append(part.strip())
            return result
        except ValueError:
            return None

    @staticmethod
    def list_manga(data: Collection):
        return "\n".join(
            f"[{index}] {manga.title} ({manga.year}) "
            f"(en: {'yes' if 'en' in manga.available_languages else 'no'})"
            for index, manga in data.items()
        )

    @property
    def locked_manga(self) -> "Manga | None":
        return self.collection[self.locked] if self.locked else None

    def e(self):
        sys.exit(0)

    def exit(self):
        self.e()

    def d(self):
        """
        Download a manga.
        """
        if not self.locked_manga:
            click.echo("No manga has been locked.")
            return
        if not self.volume_range:
            click.echo("No volumes have been chosen.")
            return

        click.echo(f"Now downloading {self.locked_manga.title}...")
        self.can_exit = True
        download(self.locked_manga, self.volume_range)

    def v(self):
        """
        Select volumes to download.
        """
        if not self.locked_manga:
            click.echo("Please select a manga first.")
            return
        volumes = self.locked_manga.aggregate()["volumes"]
        volume_list = [str(volume) for volume in volumes.keys()]

        click.echo(f"The following volumes are available: {', '.join(volume_list)}")

        click.echo(
            'What is the range of volume you\'d like to select? (If manga has "none" volume, '
            "please also add none to the list of volumes to add if you'd like to install chapters "
            "without volumes)"
        )
        input_range = click.prompt("> ", prompt_suffix="")

        to_range = self.user_range_to_list_range(input_range)
        if to_range is None:
            click.echo("Warning: Range was not parsable.")
            input_range = None
        else:
            click.echo(
                f"The following volumes will be downloaded: {', '.join(str(r) for r in to_range)}"
            )
        self.volume_range = to_range

    def _lock(self, selection: int):
        if not (0 <= selection <= len(self.collection)):
            click.echo(f"Not available. Range goes from 1 to {len(self.collection)}.")
            return

        self.locked = selection

    def debug(self):
        click.echo(
            f"COLLECTION: {self.collection}\n\n"
            f"LOCKED: {self.locked}\n"
            f"MANGA: {vars(self.locked_manga) if self.locked_manga else 'None'}\n"
            f"VOLUME SELECTED: {self.volume_range}"
        )

    def process(self, user_input: str):
        method = getattr(self, user_input, None)

        if method is not None:
            method()
        else:
            try:
                manga_selection = int(user_input)
                self._lock(manga_selection)
            except ValueError:
                click.echo('Command not found. Try "help".')

    def display_command_output(self) -> str:
        output = ""
        if self.locked:
            output += f"(M {self.locked}) "
        if self.volume_range:
            output += f"[V {' '.join([str(i) for i in self.volume_range])}] "
        output += "> "
        return output

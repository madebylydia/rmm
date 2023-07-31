import json
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, NewType

import click

from dolabella.manga import Manga, MangaChapter, MangaVolume
from dolabella.requester import download_image, get_images, search_mangas

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
TEMP_DIR = Path(tempfile.mkdtemp(prefix="dolabella_"))
print(TEMP_DIR)


def format_json(data: dict[int, Any]):
    return json.dumps(data, indent=1)


def to_safe_path(query: str):
    return re.sub(r"[^\w_. -]", "_", query)


def range_to_list(selected_range: str):
    return sum(
        (
            (
                list(range(*[int(b) + c for c, b in enumerate(a.split("-"))]))
                if "-" in a
                else [int(a)]
            )
            for a in selected_range.split(", ")
        ),
        [],
    )


def list_mangas(mangas: dict[int, Manga]):
    output = "\n------------\n".join(
        f"[{index}] {manga.title} ({manga.year})\n"
        f"ID: {manga.manga_id}\n"
        f"Has English: {'yes' if 'en' in manga.available_languages else 'no'}"
        for index, manga in mangas.items()
    )
    click.echo(output)


def convert(
    manga: Manga, volume: MangaVolume, chapter: MangaChapter, origin: Path
) -> Path:
    destination = (
        Path("~")
        / "Mangas"
        / to_safe_path(manga.title)
        / to_safe_path(volume.volume_pretty)
    ).expanduser()
    images_paths = [str(image.resolve()) for image in origin.iterdir()]

    destination.mkdir(parents=True, exist_ok=True)
    final = destination / f"{to_safe_path(chapter.chapter_pretty)}.pdf"
    if final.exists():
        click.echo(f"Warn: {final.resolve()} existed. Deleting.")
        final.unlink()

    imagemagick = shutil.which("magick")
    if not imagemagick:
        raise Exception("ImageMagick not found. Be sure to have it installed.")

    subprocess.Popen([imagemagick, *images_paths, final]).wait()

    return final


def download(manga: Manga, volumes: list[MangaVolume]):
    for volume in volumes:
        for chapter in volume.chapters:
            data = get_images(chapter.chapter_id)

            images: list[str] = data["chapter"]["dataSaver"]
            total = len(images)
            dl_folder = TEMP_DIR / manga.manga_id / volume.volume_pretty
            dl_folder.mkdir(parents=True, exist_ok=True)

            for done, image in enumerate(images, start=1):
                img = download_image(data["chapter"]["hash"], image)
                destination = dl_folder / image
                if destination.exists():
                    destination.unlink()
                destination.touch()
                destination.write_bytes(img)
                click.echo(
                    f"[V {volume.volume_pretty}] [C {chapter.chapter_pretty}] IMG {done}/{total}"
                )

            click.echo(f"Converting chapter {chapter.chapter_pretty} to PDF...")
            final = convert(manga, volume, chapter, dl_folder)
            click.echo(f"Dropped at {final.resolve()}.")


@click.command()
def mangadl() -> None:
    """
    Download a manga from MangaDex.
    """
    click.echo("What are we downloading?")
    title = click.prompt("> ", prompt_suffix="")

    data = search_mangas(title)

    if data["result"] != "ok":
        click.echo(f"Result is not ok. Cannot continue.\n{format_json(data)}")
        return
    if len(data["data"]) < 1:
        click.echo("No results found.")
        return

    mangas = {index: Manga(manga) for index, manga in enumerate(data["data"], 1)}

    click.echo(f"Found {len(mangas)} manga(s).")
    list_mangas(mangas)

    locked: int | None = None
    vol_selection: VolSelection | None = None
    should_then_leave = False
    lock_command = True

    while lock_command:
        output = ""
        if locked:
            output += f"(L {locked}) "
        if vol_selection:
            output += f"[V {vol_selection}] "
        output += "> "
        command = click.prompt(output, prompt_suffix="")

        match command:
            case "help":
                click.echo(CMDS_HELP)

            case "a":
                if not locked:
                    click.echo("A manga must be selected.")
                    continue
                click.echo(format_json(mangas[locked].aggregate()))

            case "v":
                if not locked:
                    click.echo("Can't select volume for not locked manga.")
                    continue

                lock_range = True

                while lock_range:
                    click.echo("Select range")
                    volume_range = click.prompt("> ", prompt_suffix="")

                    found = re.search(r"^(\d+)-(\d+)$", volume_range)
                    if not found:
                        click.echo(
                            'Incorrect range, must be in the following format: "START-END"'
                        )
                        continue

                    vol_selection = VolSelection(found.string)
                    lock_range = False

            case "l":
                list_mangas(mangas)

            case "d":
                if not locked:
                    click.echo("A manga must be selected.")
                    continue
                if not vol_selection:
                    click.echo("No volume selected.")
                    continue

                click.echo(f"Downloading {mangas[locked].title}...")
                lock_command = False
                should_then_leave = True

                volumes = [str(i) for i in range_to_list(vol_selection)]
                aggregated = mangas[locked].aggregate()
                has_volumes = len(aggregated["volumes"]) > 1
                if has_volumes:
                    vol_list = [
                        MangaVolume(mangas[locked], manga)
                        for manga_vol, manga in aggregated["volumes"].items()
                        if manga_vol in volumes
                    ]
                else:
                    vol_list = [
                        MangaVolume(mangas[locked], manga)
                        for manga in aggregated["volumes"].values()
                    ]
                download(mangas[locked], vol_list)

            case "i":
                if not locked:
                    click.echo("A manga must be selected.")
                    continue

                manga = mangas[locked]
                click.echo(
                    f"Title: {manga.title}\n"
                    f"ID: {manga.manga_id}\n"
                    f"Description: {manga.description}\n"
                    f"Year: {manga.year}\n"
                    f"Languages: {manga.available_languages}"
                )

            case "debug":
                click.echo(format_json(mangas))

            case "exit":
                sys.exit(0)

            case _:
                try:
                    # Possible int
                    value = int(command)
                    if 0 <= value <= len(mangas):
                        locked = value
                        continue

                    click.echo(f"Not available. Range goes from 1 to {len(mangas)}.")
                    continue

                except ValueError:
                    click.echo('Command not found. Try "help".')
                    continue

    if should_then_leave:
        return

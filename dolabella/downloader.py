import pathlib
import shutil
import subprocess
from os.path import splitext
from tempfile import mkdtemp

import click
from dolabella.core import ImageManager
from dolabella.utils import pretty_size_from_bytes, to_safe_path
from dolabella.models import Manga
from dolabella.types import DownloadPath, LockList
from dolabella.requester import download as download_image


def get_volumes_to_download(manga: Manga, lock_list: LockList):
    return sorted(
        [volume for volume in manga.get_volumes() if volume.pretty in lock_list],
        key=lambda x: x.pretty,
    )


def convert(
    drop_at: pathlib.Path, origin: pathlib.Path, chapter_pretty: str
) -> pathlib.Path:
    # sourcery skip: raise-specific-error
    images_paths = [str(image.resolve()) for image in origin.iterdir()]

    drop_at.mkdir(parents=True, exist_ok=True)
    final = drop_at / f"{to_safe_path(chapter_pretty)}.pdf"
    if final.exists():
        click.echo(f"Warn: {final.resolve()} existed. Deleting.")
        final.unlink()

    imagemagick = shutil.which("magick")
    if not imagemagick:
        raise Exception("ImageMagick not found. Be sure to have it installed.")

    subprocess.Popen([imagemagick, *images_paths, final]).wait()

    return final


def download(manga: Manga, lock_list: LockList):
    folder_tmp = pathlib.Path(mkdtemp(prefix="dolabella_"))

    volumes = get_volumes_to_download(manga, lock_list)
    folder_manga = folder_tmp / to_safe_path(manga.title)
    folder_destination = (
        pathlib.Path("~") / "Manga" / to_safe_path(manga.title)
    ).expanduser()

    for volume in volumes:
        # Loop over volumes
        click.echo(f"Now downloading volume {volume.pretty}.")
        folder_volume = folder_manga / to_safe_path(volume.pretty)
        click.echo(f"{len(volume.chapters)} chapters will be downloaded.")

        for chapter in volume.chapters:
            # Loop over volume's chapters
            click.echo(f"Now downloading chapter {chapter.pretty}.")

            # Initialize a manager for this volume
            folder_chapter = folder_volume / to_safe_path(chapter.pretty)
            manager = ImageManager(DownloadPath(folder_chapter))

            at_home = chapter.get_images()
            hash = at_home["chapter"]["hash"]

            for page, image in enumerate(at_home["chapter"]["dataSaver"], start=1):
                # Download images one by one from MangaDex
                _, ext = splitext(image)
                raw_image = download_image(hash, image)
                manager.push(page, volume.pretty, raw_image, ext[1:])

                click.echo(
                    f"[V {volume.pretty}] [C {chapter.pretty}] "
                    f"IMG {page}/{len(at_home['chapter']['dataSaver'])}"
                )

            click.echo(
                f"Converting {chapter.pretty} to PDF... This might take a while..."
            )
            dropped_at = convert(folder_destination, folder_chapter, chapter.pretty)
            click.echo(f'Done! It has been dropped at "{dropped_at.resolve()}".')
            click.echo(
                f"Now cleaning {pretty_size_from_bytes(manager.size())} from temporary folder..."
            )
            manager.cleanup()

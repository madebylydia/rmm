import pathlib
import re

import cuid2

from dolabella.models import Manga, Volume
from dolabella.types import DownloadPath

import shutil

FILE_PATTERN_REGEX = re.compile(r"^(\S+)-(\S+)-(\S+)$")


class ImageManager(object):
    """
    Create an instance of ImageManager that will manage images in a given folder.

    Goal is that this class will take care of adding, ordering and deleting a folder
    for the sake of good management.
    """

    def __init__(self, path: DownloadPath) -> None:
        self.path = path

        if not self.path.exists():
            self.path.mkdir(parents=True)

    def push(self, page: int, volume: str, data: bytes, extension: str):
        final_path = (
            self.path / f"{volume}-{page}-{cuid2.Cuid().generate()}.{extension}"
        )
        final_path.touch()
        final_path.write_bytes(data)

    def available_images(self) -> dict[int, pathlib.Path]:
        images: dict[int, pathlib.Path] = {}
        for file in self.path.iterdir():
            image_indice = self.image_page(file)
            images[image_indice] = file
        return images

    @staticmethod
    def image_page(path_to_image: pathlib.Path):
        """
        Attempt to determine a image's page through his file's name.
        """
        name = path_to_image.stem
        if match := FILE_PATTERN_REGEX.match(name):
            return int(match.group(2))
        else:
            raise NameError(f'File "{name}" does not match file pattern.')

    def size(self):
        return float(
            sum(file.stat().st_size for file in pathlib.Path(self.path).rglob("*"))
        )

    def cleanup(self):
        shutil.rmtree(self.path)

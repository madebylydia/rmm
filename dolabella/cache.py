from typing import Any
from tempfile import mkdtemp
from pathlib import Path

from dolabella.manga import Manga, MangaChapter


class CachedChapter:
    def __init__(self) -> None:
        self.manga: dict[str, Any]
        self.name = self.manga["attributes"]
        self.dir = Path(mkdtemp("Dolabella"))

    def push(self, manga: Manga, chapter: MangaChapter):
        manga_path = self.dir / manga.manga_id

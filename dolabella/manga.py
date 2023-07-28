from typing import Any

import click

from dolabella.requester import aggregate_manga


class Manga:
    manga: dict[str, Any]

    def __init__(self, manga: dict[str, Any]) -> None:
        self.manga = manga

    @property
    def manga_id(self) -> str:
        return self.manga["id"]

    @property
    def title(self) -> str:
        attr = self.manga["attributes"]["title"]
        return attr.get("en", next(iter(attr)))

    @property
    def description(self) -> str:
        desc = self.manga["attributes"]["description"]
        return desc.get("en", next(iter(desc)))

    @property
    def year(self) -> int:
        return self.manga["attributes"]["year"]

    @property
    def available_languages(self) -> list[str]:
        return self.manga["attributes"]["availableTranslatedLanguages"]

    def aggregate(self):
        return aggregate_manga(self.manga_id)


class MangaVolume:
    manga: Manga

    def __init__(self, manga: Manga, volume: dict[str, Any]) -> None:
        self.manga = manga
        self.volume = volume

    @property
    def count(self):
        return self.volume["count"]

    @property
    def volume_pretty(self) -> str:
        return self.volume["volume"]

    @property
    def chapters(self):
        return [MangaChapter(chapter) for chapter in self.volume["chapters"].values()]


class MangaChapter:
    chapter: dict[str, Any]

    def __init__(self, chapter: dict[str, Any]) -> None:
        self.chapter = chapter

    @property
    def chapter_pretty(self) -> str:
        return self.chapter["chapter"]

    @property
    def chapter_id(self) -> str:
        return self.chapter["id"]

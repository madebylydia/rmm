import typing

import requests

from dolabella.types import MangaRating, MangaStatus

BASE_URL = "https://api.mangadex.org"


class MangaAttributes(typing.TypedDict):
    title: dict[str, str]
    description: dict[str, str]
    original_language: str
    status: MangaStatus
    year: int | None
    contentRating: MangaRating
    availableTranslatedLanguages: list[str]


class Manga(typing.TypedDict):
    id: str
    type: typing.Literal["manga"]
    attributes: MangaAttributes


class MangaSearchResponse(typing.TypedDict):
    result: typing.Literal["ok", "error"]
    response: typing.Literal["collection"]
    data: list[Manga]


def search_mangas(query: str) -> MangaSearchResponse:
    return requests.get(f"{BASE_URL}/manga", params={"title": query}).json()


class AggregateVolumeChapters(typing.TypedDict):
    chapter: str
    id: str
    others: list[str]
    count: int


class AggregateVolume(typing.TypedDict):
    volume: str
    count: int
    chapters: dict[str, AggregateVolumeChapters]


class AggregateResponse(typing.TypedDict):
    result: typing.Literal["ok", "error"]
    volumes: dict[int | typing.Literal["none"], AggregateVolume]


def aggregate_manga(manga_id: str) -> AggregateResponse:
    return requests.get(
        f"{BASE_URL}/manga/{manga_id}/aggregate",
        params={"translatedLanguage[]": ["en"]},
    ).json()


class AtHomeChapter(typing.TypedDict):
    hash: str
    data: list[str]
    dataSaver: list[str]


class AtHomeResponse(typing.TypedDict):
    result: typing.Literal["ok", "error"]
    baseUrl: str
    chapter: AtHomeChapter


def get_images(chapter_id: str) -> AtHomeResponse:
    return requests.get(f"{BASE_URL}/at-home/server/{chapter_id}").json()


def download(hash: str, filename: str) -> bytes:
    return requests.get(
        f"https://uploads.mangadex.org/data-saver/{hash}/{filename}"
    ).content

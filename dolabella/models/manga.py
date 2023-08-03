from functools import lru_cache

from dolabella.models.chapter import Chapter
from dolabella.models.volume import Volume
from dolabella.requester import AggregateResponse, aggregate_manga
from dolabella.types import MangaRating, MangaStatus


class Manga(object):
    manga_id: str
    title: str
    year: int | None
    description: str
    status: MangaStatus
    rating: MangaRating
    available_languages: list[str]

    def __init__(
        self,
        manga_id: str,
        title: str,
        description: str,
        year: int | None,
        status: MangaStatus,
        rating: MangaRating,
        available_languages: list[str],
    ) -> None:
        self.manga_id = manga_id
        self.title = title
        self.description = description
        self.year = year
        self.status = status
        self.rating = rating
        self.available_languages = available_languages

    def get_volumes(self) -> list[Volume]:
        aggregated = self.aggregate()

        volumes = []
        for volume in aggregated["volumes"].values():
            chapters = volume["chapters"]
            volumes.append(
                Volume(
                    volume["volume"],
                    sorted(
                        [
                            Chapter(chapter["chapter"], chapter["id"])
                            for chapter in chapters.values()
                        ],
                        key=lambda x: x.pretty,
                        reverse=True,
                    ),
                )
            )
        return volumes

    @lru_cache()
    def aggregate(self) -> AggregateResponse:
        return aggregate_manga(self.manga_id)

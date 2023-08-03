import pathlib
from typing import TYPE_CHECKING, Literal, NewType, TypeAlias

if TYPE_CHECKING:
    from dolabella.models import Manga


DownloadPath = NewType("DownloadPath", pathlib.Path)

Collection = NewType("Collection", dict[int, "Manga"])

LockList = NewType("LockList", list[str | Literal["none"]])

MangaStatus: TypeAlias = Literal["completed", "ongoing", "cancelled", "hiatus"]
MangaRating: TypeAlias = Literal["safe", "suggestive", "erotica", "pornographic"]

import typing


if typing.TYPE_CHECKING:
    from dolabella.models import Chapter


class Volume:
    pretty: str

    def __repr__(self) -> str:
        return f"<Volume pretty={self.pretty}>"

    def __init__(self, pretty: str, chapters: "list[Chapter]") -> None:
        self.pretty = pretty
        self.chapters = chapters

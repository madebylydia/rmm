from dolabella.requester import get_images


class Chapter:
    pretty: str
    chapter_id: str

    def __init__(self, pretty: str, chapter_id: str) -> None:
        self.pretty = pretty
        self.chapter_id = chapter_id

    def get_images(self):
        return get_images(self.chapter_id)

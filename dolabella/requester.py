import requests

BASE_URL = "https://api.mangadex.org"


def search_mangas(query: str):
    return requests.get(f"{BASE_URL}/manga", params={"title": query}).json()


def aggregate_manga(manga_id: str):
    return requests.get(
        f"{BASE_URL}/manga/{manga_id}/aggregate",
        params={"translatedLanguage[]": ["en"]},
    ).json()


def get_images(chapter_id: str):
    return requests.get(f"{BASE_URL}/at-home/server/{chapter_id}").json()


def download_image(hash: str, image_url: str):
    return requests.get(
        f"https://uploads.mangadex.org/data-saver/{hash}/{image_url}"
    ).content

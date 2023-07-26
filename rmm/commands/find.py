import click
import requests


@click.command()
@click.argument("name")
def find(name: str):
    print("Requesting...")

    base_url = "https://api.mangadex.org"
    r = requests.get(f"{base_url}/manga", params={"title": name, "limit": 5})

    data = r.json()["data"]
    print(f"Found {len(data)} manga(s).")

    to_see = [
        f"Name: {manga['attributes']['title'].get('en')}\n"
        f"Link: https://mangadex.org/title/{manga['id']}"
        for manga in data
    ]

    print("\n\n".join(to_see))

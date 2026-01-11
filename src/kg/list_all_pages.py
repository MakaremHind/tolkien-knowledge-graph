import requests
from urllib.parse import quote
from pathlib import Path

API_URL = "https://tolkiengateway.net/w/api.php"

OUT_FILE = Path("data/pages.ttl")

PREFIXES = """@prefix ex: <http://example.org/tolkien/> .
@prefix schema: <https://schema.org/> .

"""


def safe_uri(title: str) -> str:
    return quote(title.replace(" ", "_"))


def fetch_all_pages():
    session = requests.Session()
    params = {
        "action": "query",
        "list": "allpages",
        "aplimit": "max",
        "format": "json",
    }

    while True:
        response = session.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        for page in data["query"]["allpages"]:
            yield page["title"]

        if "continue" not in data:
            break

        params.update(data["continue"])


def main():
    OUT_FILE.write_text(PREFIXES, encoding="utf-8")

    with OUT_FILE.open("a", encoding="utf-8") as out:
        for title in fetch_all_pages():
            page_uri = f"ex:page/{safe_uri(title)}"
            res_uri = f"ex:resource/{safe_uri(title)}"

            out.write(
                f"""{page_uri} a schema:WebPage ;
    schema:name "{title}" ;
    schema:about {res_uri} .

{res_uri} a schema:Thing ;
    schema:name "{title}" .

"""
            )

    print(f"✔ Pages graph written to {OUT_FILE}")


if __name__ == "__main__":
    main()

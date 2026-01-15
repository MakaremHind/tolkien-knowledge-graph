import requests

API_URL = "https://tolkiengateway.net/w/api.php"

HEADERS = {
    "User-Agent": "TolkienKG/1.0 (academic project; contact: student)"
}


def fetch_wikitext(title: str) -> str:
    params = {
        "action": "parse",
        "page": title,
        "prop": "wikitext",
        "format": "json"
    }

    response = requests.get(API_URL, params=params, headers=HEADERS)
    response.raise_for_status()

    data = response.json()
    return data["parse"]["wikitext"]["*"]


# Optional: keep this for manual testing
if __name__ == "__main__":
    wikitext = fetch_wikitext("Elrond")
    with open("data/elrond.wikitext", "w", encoding="utf-8") as f:
        f.write(wikitext)

    print("Elrond wikitext saved to data/elrond.wikitext")

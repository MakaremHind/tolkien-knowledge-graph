import requests

API_URL = "https://tolkiengateway.net/w/api.php"

params = {
    "action": "parse",
    "page": "Elrond",
    "prop": "wikitext",
    "format": "json"
}

headers = {
    # REQUIRED by Wikimedia policy
    "User-Agent": "TolkienKG/1.0 (academic project; contact: student)"
}

response = requests.get(API_URL, params=params, headers=headers)
response.raise_for_status()

data = response.json()
wikitext = data["parse"]["wikitext"]["*"]

with open("data/elrond.wikitext", "w", encoding="utf-8") as f:
    f.write(wikitext)

print("Elrond wikitext saved to data/elrond.wikitext")

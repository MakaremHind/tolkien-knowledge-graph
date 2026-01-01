import requests

API_URL = "https://tolkiengateway.net/w/api.php"

params = {
    "action": "query",
    "list": "categorymembers",
    "cmtitle": "Category:Third_Age_characters",
    "cmlimit": "max",
    "format": "json"
}

headers = {
    "User-Agent": "TolkienKG/1.0 (academic project; contact: student)"
}

response = requests.get(API_URL, params=params, headers=headers)
response.raise_for_status()

data = response.json()

titles = [
    page["title"]
    for page in data["query"]["categorymembers"]
    if not page["title"].startswith("Category:")
]

print(f"Found {len(titles)} Third Age characters")

with open("data/third_age_characters.txt", "w", encoding="utf-8") as f:
    for t in titles:
        f.write(t + "\n")

print("Saved to data/third_age_characters.txt")

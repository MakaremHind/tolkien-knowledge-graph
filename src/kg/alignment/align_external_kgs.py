from rdflib import Graph, Namespace, URIRef
from pathlib import Path
import requests
from urllib.parse import unquote

# =========================
# Namespaces
# =========================

SCHEMA = Namespace("https://schema.org/")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
EX = Namespace("http://example.org/tolkien/")

# =========================
# Files
# =========================

DATA_FILE = Path("data/knowledge_graph_final.ttl")
OUT_FILE = Path("data/alignment_external.ttl")

# =========================
# HTTP config
# =========================

HEADERS = {
    "User-Agent": "TolkienKGAlignmentBot/1.0 (academic project; contact: student@example.org)"
}

WIKIPEDIA_API = "https://en.wikipedia.org/w/api.php"

# =========================
# Helpers
# =========================

def wikipedia_page_exists(title: str) -> bool:
    print(f"    → Checking Wikipedia API for title: {title}")

    params = {
        "action": "query",
        "titles": title,
        "format": "json"
    }

    try:
        r = requests.get(
            WIKIPEDIA_API,
            params=params,
            headers=HEADERS,
            timeout=10
        )

        print(f"    → HTTP status: {r.status_code}")
        print(f"    → Content-Type: {r.headers.get('Content-Type')}")

        # Debug: show raw text if something is wrong
        if "application/json" not in r.headers.get("Content-Type", ""):
            print("    ✗ Response is not JSON:")
            print(r.text[:300])
            return False

        data = r.json()
        pages = data.get("query", {}).get("pages", {})
        page_id = next(iter(pages.keys()))

        if page_id == "-1":
            print("    ✗ Wikipedia page does NOT exist")
            return False

        print("    ✔ Wikipedia page exists")
        return True

    except Exception as e:
        print(f"    ✗ Exception while querying Wikipedia API: {e}")
        return False


def wikipedia_uri(title: str) -> URIRef:
    return URIRef(f"https://en.wikipedia.org/wiki/{title}")


def dbpedia_uri(title: str) -> URIRef:
    return URIRef(f"http://dbpedia.org/resource/{title}")


def yago_uri(title: str) -> URIRef:
    return URIRef(f"http://yago-knowledge.org/resource/{title}")


# =========================
# Main logic
# =========================

def main():
    print("========== START ALIGNMENT ==========")

    print(f"Loading RDF graph from: {DATA_FILE}")
    g = Graph()
    g.parse(DATA_FILE)
    print(f"✔ RDF graph loaded with {len(g)} triples\n")

    out = Graph()
    out.bind("ex", EX)
    out.bind("owl", OWL)

    sameas_count = 0
    tg_count = 0
    align_count = 0

    print("Scanning for schema:sameAs triples...\n")

    for entity, _, tg_url in g.triples((None, SCHEMA.sameAs, None)):
        sameas_count += 1
        tg_url = str(tg_url)

        if "tolkiengateway.net/wiki/" not in tg_url:
            continue

        tg_count += 1

        page_title = unquote(tg_url.split("/wiki/")[-1])

        print("Found sameAs triple:")
        print(f"  entity = {entity}")
        print(f"  sameAs = {tg_url}")
        print(f"  → Tolkien Gateway page title: {page_title}")

        if not wikipedia_page_exists(page_title):
            print("  ✗ No Wikipedia page found\n")
            continue

        wiki = wikipedia_uri(page_title)
        dbpedia = dbpedia_uri(page_title)
        yago = yago_uri(page_title)

        out.add((entity, OWL.sameAs, wiki))
        out.add((entity, OWL.sameAs, dbpedia))
        out.add((entity, OWL.sameAs, yago))

        align_count += 1
        print("  ✔ Alignment added\n")

    out.serialize(OUT_FILE, format="turtle")

    print("========== SUMMARY ==========")
    print(f"schema:sameAs triples found: {sameas_count}")
    print(f"Tolkien Gateway links found: {tg_count}")
    print(f"Alignments written: {align_count}")
    print(f"\n✔ Output written to: {OUT_FILE}")
    print("========== DONE ==========")


if __name__ == "__main__":
    main()

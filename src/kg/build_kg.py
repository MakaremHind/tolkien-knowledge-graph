from pathlib import Path

from fetch_elrond_wikitext import fetch_wikitext
from parse_infobox import extract_infobox
from infobox_to_dict import infobox_to_dict
from infobox_mapping import FIELD_MAPPING as CHARACTER_MAPPING
from infobox_actor_mapping import FIELD_MAPPING as ACTOR_MAPPING
from character_to_rdf import character_to_rdf
from place_to_rdf import place_infobox_to_rdf


# =========================
# CONFIGURATION
# =========================

CHARACTER_LIST = Path("data/third_age_characters.txt")
PLACE_LIST = Path("data/places.txt")  # optional, can start with manual list
OUT_FILE = Path("data/knowledge_graph.ttl")

PREFIXES = """@prefix ex: <http://example.org/tolkien/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .

"""


# =========================
# TEMPLATE DISPATCH TABLE
# Order matters: first match wins
# =========================

TEMPLATES = [
    (
        "Infobox character",
        lambda title, infobox: character_to_rdf(
            title, infobox, CHARACTER_MAPPING
        ),
    ),
    (
        "Actor",
        lambda title, infobox: character_to_rdf(
            title, infobox, ACTOR_MAPPING
        ),
    ),
    (
        "Location infobox",
        place_infobox_to_rdf,
    ),
]




# =========================
# CORE LOGIC
# =========================

def process_title(title: str) -> str | None:
    """
    Fetch a wiki page, detect supported infobox,
    and return Turtle RDF string or None.
    """
    wikitext = fetch_wikitext(title)

    for template_name, rdf_fn in TEMPLATES:
        infobox_text = extract_infobox(wikitext, template_name)
        if infobox_text:
            infobox = infobox_to_dict(infobox_text)
            return rdf_fn(title, infobox)

    print(f"  ⚠ No supported infobox found for: {title}")
    return None


def process_list(path: Path, out):
    """
    Process a list of page titles and append RDF.
    """
    with path.open(encoding="utf-8") as f:
        for i, title in enumerate(f, start=1):
            title = title.strip()
            if not title:
                continue

            print(f"[{i}] Processing {title}")

            try:
                rdf = process_title(title)
                if rdf:
                    out.write(rdf + "\n\n")
            except Exception as e:
                print(f"  Error for {title}: {e}")


# =========================
# MAIN
# =========================

def main():
    OUT_FILE.write_text(PREFIXES, encoding="utf-8")

    with OUT_FILE.open("a", encoding="utf-8") as out:
        # Characters
        if CHARACTER_LIST.exists():
            print("=== Processing characters ===")
            process_list(CHARACTER_LIST, out)

        # Places (optional)
        if PLACE_LIST.exists():
            print("=== Processing places ===")
            process_list(PLACE_LIST, out)

    print(f"\n✔ Knowledge Graph written to {OUT_FILE}")


if __name__ == "__main__":
    main()

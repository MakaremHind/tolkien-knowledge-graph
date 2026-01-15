from pathlib import Path
from urllib.parse import quote

from fetch_elrond_wikitext import fetch_wikitext
from parse_infobox import extract_infobox
from infobox_to_dict import infobox_to_dict
from infobox_mapping import FIELD_MAPPING as CHARACTER_MAPPING
from infobox_actor_mapping import FIELD_MAPPING as ACTOR_MAPPING

from character_to_rdf import character_to_rdf
from place_to_rdf import place_infobox_to_rdf
from actor_to_rdf import actor_infobox_to_rdf
from author_to_rdf import author_to_rdf
from person_to_rdf import person_to_rdf
from organization_to_rdf import organization_infobox_to_rdf
from film_to_rdf import film_to_rdf
from book_to_rdf import book_to_rdf


# =========================
# CONFIGURATION
# =========================

CHARACTER_LIST = Path("data/third_age_characters.txt")
PLACE_LIST = Path("data/places.txt")
OUT_FILE = Path("data/knowledge_graph.ttl")
ACTOR_LIST = Path("data/actors.txt")
ORGANIZATION_LIST = Path("data/organizations.txt")
FILM_LIST = Path("data/films.txt")
BOOK_LIST = Path("data/books.txt")

PREFIXES = """@prefix ex: <http://example.org/tolkien/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .

"""


# =========================
# TEMPLATE DISPATCH TABLE
# =========================

TEMPLATES = [
    # Fictional characters
    (
        "Infobox character",
        lambda title, infobox: character_to_rdf(
            title, infobox, CHARACTER_MAPPING
        ),
    ),

    # Films
    ("film infobox", film_to_rdf),
    ("Film infobox", film_to_rdf),

    # Books
    ("Book", book_to_rdf),

    # Real-world people
    ("Actor", actor_infobox_to_rdf),
    ("Person infobox", person_to_rdf),

    # Authors
    ("Author infobox", author_to_rdf),
    ("Author_infobox", author_to_rdf),
    ("author infobox", author_to_rdf),
    ("author_infobox", author_to_rdf),

    # Organizations
    ("Organization infobox", organization_infobox_to_rdf),
    ("organization infobox", organization_infobox_to_rdf),
    ("Infobox organization", organization_infobox_to_rdf),
    ("infobox organization", organization_infobox_to_rdf),
    ("Organisation infobox", organization_infobox_to_rdf),
    ("Society infobox", organization_infobox_to_rdf),
    ("Group infobox", organization_infobox_to_rdf),

    # Places
    ("Location infobox", place_infobox_to_rdf),
]


# =========================
# HELPER: page ↔ resource link (Option C)
# =========================

def page_resource_link(title: str) -> str:
    """
    Create schema:sameAs link between curated entity and generic resource entity
    (DBpedia-style modelling)
    """
    safe = quote(title.replace(" ", "_"))
    return f'ex:{safe} schema:sameAs ex:resource/{safe} .'


# =========================
# CORE LOGIC
# =========================

def process_title(title: str) -> str | None:
    wikitext = fetch_wikitext(title)

    for template_name, rdf_fn in TEMPLATES:
        try:
            infobox_text = extract_infobox(wikitext, template_name)
        except Exception:
            print(f"  Skipping {title} due to infobox parse error")
            return None

        if infobox_text:
            infobox = infobox_to_dict(infobox_text)
            rdf = rdf_fn(title, infobox)

            # 🔹 Option C: link curated entity to generic resource
            link = page_resource_link(title)

            return rdf + "\n" + link

    print(f" No supported infobox found for: {title}")
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
        if CHARACTER_LIST.exists():
            print("=== Processing characters ===")
            process_list(CHARACTER_LIST, out)

        if FILM_LIST.exists():
            print("=== Processing films ===")
            process_list(FILM_LIST, out)

        if BOOK_LIST.exists():
            print("=== Processing books ===")
            process_list(BOOK_LIST, out)

        if ACTOR_LIST.exists():
            print("=== Processing actors ===")
            process_list(ACTOR_LIST, out)

        if ORGANIZATION_LIST.exists():
            print("=== Processing organizations ===")
            process_list(ORGANIZATION_LIST, out)

        if PLACE_LIST.exists():
            print("=== Processing places ===")
            process_list(PLACE_LIST, out)

    print(f"\nKnowledge Graph written to {OUT_FILE}")


if __name__ == "__main__":
    main()

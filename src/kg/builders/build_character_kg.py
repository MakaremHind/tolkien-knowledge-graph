from pathlib import Path

from fetch_elrond_wikitext import fetch_wikitext
from parse_infobox import extract_infobox
from infobox_to_dict import infobox_to_dict
from character_to_rdf import character_to_rdf


CHAR_LIST = Path("data/third_age_characters.txt")
OUT_FILE = Path("data/characters.ttl")

PREFIXES = """@prefix ex: <http://example.org/tolkien/> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix schema: <https://schema.org/> .

"""


def main():
    OUT_FILE.write_text(PREFIXES, encoding="utf-8")

    with CHAR_LIST.open(encoding="utf-8") as f:
        for i, title in enumerate(f, start=1):
            title = title.strip()
            if not title:
                continue

            print(f"[{i}] Processing {title}")

            try:
                wikitext = fetch_wikitext(title)
                infobox_txt = extract_infobox(wikitext)

                if not infobox_txt:
                    print(f"  ⚠ No infobox found for {title}")
                    continue

                infobox = infobox_to_dict(infobox_txt)
                rdf = character_to_rdf(title, infobox)

                with OUT_FILE.open("a", encoding="utf-8") as out:
                    out.write(rdf + "\n\n")

            except Exception as e:
                print(f"  ❌ Error for {title}: {e}")


if __name__ == "__main__":
    main()

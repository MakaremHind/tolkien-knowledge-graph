from urllib.parse import quote
from infobox_film_mapping import FIELD_MAPPING


def safe_uri(title: str) -> str:
    return quote(title.replace(" ", "_"))


def film_to_rdf(title: str, infobox: dict) -> str:
    subject = f"ex:{safe_uri(title)}"

    lines = [
        f"{subject} a schema:Movie ;",
        f'    rdfs:label "{title}"@en ;',
        f'    schema:name "{title}" ;',
        f"    schema:sameAs <https://tolkiengateway.net/wiki/{safe_uri(title)}> ;",
    ]

    for field, predicate in FIELD_MAPPING.items():
        value = infobox.get(field)

        # Fix 3: skip empty values
        if not value:
            continue

        value = value.replace('"', '\\"').strip()

        # Fix 2 (partial): skip garbage website-style values
        if field == "website" and not value.startswith("http"):
            continue

        lines.append(f'    {predicate} "{value}" ;')

    # Replace final semicolon
    lines[-1] = lines[-1].rstrip(" ;") + " ."

    return "\n".join(lines)

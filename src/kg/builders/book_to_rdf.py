from urllib.parse import quote
from infobox_book_mapping import FIELD_MAPPING

def safe_uri(name: str) -> str:
    return quote(name.replace(" ", "_"))

def book_to_rdf(title: str, infobox: dict) -> str:
    subject = f"ex:{safe_uri(title)}"

    lines = [
        f"{subject} a schema:Book ;",
        f'    rdfs:label "{title}"@en ;',
        f'    schema:name "{title}" ;',
        f"    schema:sameAs <https://tolkiengateway.net/wiki/{safe_uri(title)}> ;",
    ]

    for field, predicate in FIELD_MAPPING.items():
        value = infobox.get(field)
        if not value:
            continue

        value = value.replace('"', '\\"').strip()
        lines.append(f'    {predicate} "{value}" ;')

    lines[-1] = lines[-1].rstrip(" ;") + " ."
    return "\n".join(lines)

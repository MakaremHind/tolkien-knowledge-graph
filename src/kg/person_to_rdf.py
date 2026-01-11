from urllib.parse import quote
from infobox_person_mapping import FIELD_MAPPING



def safe_uri(name: str) -> str:
    return name.replace(" ", "_")

def person_to_rdf(title: str, infobox: dict) -> str:
    subject = f"ex:{safe_uri(title)}"

    lines = [
        f"{subject} a schema:Person ;",
        f'    rdfs:label "{title}"@en ;',
        f'    schema:name "{title}" ;',
        f"    schema:sameAs <https://tolkiengateway.net/wiki/{safe_uri(title)}> ;",
    ]

    for field, predicate in FIELD_MAPPING.items():
        value = infobox.get(field)

        # Fix 3 — no empty literals
        if not value:
            continue

        value = value.replace('"', '\\"').strip()

        # Fix 2 — prevent bad website literals
        if field == "website" and not value.startswith("http"):
            continue

        lines.append(f'    {predicate} "{value}" ;')

    # Replace last semicolon with dot
    lines[-1] = lines[-1].rstrip(" ;") + " ."

    return "\n".join(lines)

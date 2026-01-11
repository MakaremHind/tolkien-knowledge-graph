from urllib.parse import quote
from infobox_organization_mapping import FIELD_MAPPING

def safe_uri(name: str) -> str:
    return quote(name.replace(" ", "_"))

def organization_infobox_to_rdf(title: str, infobox: dict) -> str:
    subject = f"ex:{safe_uri(title)}"

    lines = [
        f"{subject} a schema:Organization ;",
        f'    rdfs:label "{title}"@en ;',
        f'    schema:name "{title}" ;',
        f"    schema:sameAs <https://tolkiengateway.net/wiki/{safe_uri(title)}> ;",
    ]

    for field, predicate in FIELD_MAPPING.items():
        value = infobox.get(field)
        if not value:
            continue  # ✅ Fix 3: skip empty values

        value = value.replace('"', '\\"').strip()
        lines.append(f'    {predicate} "{value}" ;')

    # replace last semicolon
    lines[-1] = lines[-1].rstrip(" ;") + " ."

    return "\n".join(lines)

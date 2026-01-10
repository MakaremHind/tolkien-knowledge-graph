from urllib.parse import quote
from infobox_place_mapping import FIELD_MAPPING

def safe_uri(name: str) -> str:
    """Make a safe URI fragment."""
    return quote(name.replace(" ", "_"))

def place_infobox_to_rdf(title: str, infobox: dict) -> str:
    """
    Generate a Turtle RDF snippet for a place
    given a title and a parsed infobox dict.
    """
    subject = f"ex:{safe_uri(title)}"

    lines = [f"{subject} a schema:Place ;"]
    lines.append(f'    rdfs:label "{title}"@en ;')
    lines.append(f'    schema:sameAs <https://tolkiengateway.net/wiki/{safe_uri(title)}> ;')

    for field, predicate in FIELD_MAPPING.items():
        if field not in infobox:
            continue
        value = infobox[field].strip()
        if not value:
            continue

        # Clean wiki markup lightly here (strip [[]], refs, etc.)
        clean_val = (
            value.replace("[[", "").replace("]]", "").replace("<ref>", "").replace("</ref>", "")
        )
        lines.append(f'    {predicate} "{clean_val}" ;')

    lines[-1] = lines[-1].rstrip(" ;") + " ."
    return "\n".join(lines)

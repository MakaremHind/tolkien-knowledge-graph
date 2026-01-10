from urllib.parse import quote
import re

from infobox_mapping import FIELD_MAPPING


def safe_uri(name: str) -> str:
    """Turn a page title into a safe URI fragment."""
    return quote(name.replace(" ", "_"))


def clean_value(value: str) -> str:
    """
    Light DBpedia-style cleaning:
    - remove <ref>...</ref>
    - remove [[...]] markup (keep label)
    """
    # Remove <ref>...</ref>
    value = re.sub(r"<ref[^>]*>.*?</ref>", "", value)

    # Replace [[A|B]] → B, [[A]] → A
    value = re.sub(r"\[\[([^|\]]+)\|([^\]]+)\]\]", r"\2", value)
    value = re.sub(r"\[\[([^\]]+)\]\]", r"\1", value)

    return value.strip()


def character_to_rdf(title: str, infobox: dict, field_mapping: dict) -> str:
    """
    Convert a character infobox dictionary to Turtle RDF.
    Returns Turtle WITHOUT prefixes.
    """
    subject = f"ex:{safe_uri(title)}"

    lines = [
        f"{subject} a schema:Person ;",
        f'    rdfs:label "{title}"@en ;',
        f'    schema:name "{title}" ;',
        f"    schema:sameAs <https://tolkiengateway.net/wiki/{safe_uri(title)}> ;",
    ]

    for field, predicate in field_mapping.items():
        if field not in infobox:
            continue

        value = infobox[field].strip()
        if not value:
            continue  # skip empty values

        value = clean_value(value)
        value = value.replace('"', '\\"')

        lines.append(f'    {predicate} "{value}" ;')

    # Replace last semicolon with dot
    lines[-1] = lines[-1].rstrip(" ;") + " ."

    return "\n".join(lines)

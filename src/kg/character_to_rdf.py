from urllib.parse import quote

from infobox_mapping import FIELD_MAPPING


def safe_uri(name: str) -> str:
    """
    Turn a page title into a safe URI fragment.
    """
    return quote(name.replace(" ", "_"))


def character_to_rdf(title: str, infobox: dict) -> str:
    """
    Convert a character infobox dictionary to Turtle RDF.
    Returns a Turtle string (without prefixes).
    """
    subject = f"ex:{safe_uri(title)}"

    lines = [f"{subject} a schema:Person ;"]
    lines.append(f'    rdfs:label "{title}"@en ;')
    lines.append(f'    schema:name "{title}" ;')
    lines.append(f"    schema:sameAs <https://tolkiengateway.net/wiki/{safe_uri(title)}> ;")

    for field, predicate in FIELD_MAPPING.items():
        if field not in infobox:
            continue

        value = infobox[field]
        value = value.replace('"', '\\"')

        lines.append(f'    {predicate} "{value}" ;')

    # Replace last semicolon with a dot
    lines[-1] = lines[-1].rstrip(" ;") + " ."

    return "\n".join(lines)


# Optional standalone test
if __name__ == "__main__":
    sample = {
        "gender": "Male",
        "species": "Half-elf",
        "location": "Rivendell"
    }

    print(character_to_rdf("Elrond", sample))

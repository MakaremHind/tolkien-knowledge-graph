from urllib.parse import quote
from infobox_actor_mapping import FIELD_MAPPING


def safe_uri(name: str) -> str:
    return quote(name.replace(" ", "_"))

def extract_url(text: str) -> str | None:
    """
    Extract a URL from wiki-style external links.
    Example: [https://imdb.com/name/nm0000704/ Profile]
    """
    if "http" not in text:
        return None

    url = text[text.find("http"):]
    url = url.split()[0]      # stop at first space
    return url.rstrip("]")    # remove closing bracket


def actor_infobox_to_rdf(title: str, infobox: dict) -> str:
    subject = f"ex:{safe_uri(title)}"

    lines = [
        f"{subject} a schema:Person ;",
        f'    rdfs:label "{title}"@en ;',
        f'    schema:name "{title}" ;',
        f"    schema:sameAs <https://tolkiengateway.net/wiki/{safe_uri(title)}> ;"
    ]

    for field, predicate in FIELD_MAPPING.items():
        if field not in infobox:
            continue

        value = infobox[field].strip()
        if not value:
            continue

        # IMDb special case → IRI, not literal
        if field == "imdb":
            url = extract_url(value)
            if url:
                lines.append(f"    schema:sameAs <{url}> ;")
            continue

        value = value.replace('"', '\\"')
        lines.append(f'    {predicate} "{value}" ;')


    lines[-1] = lines[-1].rstrip(" ;") + " ."
    return "\n".join(lines)

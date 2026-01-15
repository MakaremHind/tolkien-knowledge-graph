import re


def extract_infobox(wikitext: str, template_name: str) -> str | None:
    """
    Extracts a given infobox template from wikitext.

    Example template_name:
    - "Infobox character"
    - "Location infobox"
    """

    # Match {{Template name | ... }}
    pattern = re.compile(
        r"\{\{\s*" + re.escape(template_name) + r"\s*\|",
        re.IGNORECASE
    )

    match = pattern.search(wikitext)
    if not match:
        return None

    start = match.start()
    depth = 0

    for i in range(start, len(wikitext)):
        if wikitext[i:i+2] == "{{":
            depth += 1
        elif wikitext[i:i+2] == "}}":
            depth -= 1
            if depth == 0:
                return wikitext[start:i+2]

    return None

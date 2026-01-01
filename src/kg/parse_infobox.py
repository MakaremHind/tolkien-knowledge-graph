import re


def extract_infobox(wikitext: str) -> str | None:
    """
    Extracts the {{Infobox character ...}} template from wikitext.
    Returns the raw infobox text (without outer braces), or None if not found.
    """

    pattern = re.compile(
        r"\{\{\s*Infobox character\s*(.*?)\n\}\}",
        re.DOTALL | re.IGNORECASE
    )

    match = pattern.search(wikitext)
    if not match:
        return None

    return match.group(1)


# Optional standalone test
if __name__ == "__main__":
    with open("data/elrond.wikitext", encoding="utf-8") as f:
        text = f.read()

    infobox = extract_infobox(text)

    if infobox:
        with open("data/elrond_infobox.txt", "w", encoding="utf-8") as out:
            out.write(infobox)
        print("Infobox extracted to data/elrond_infobox.txt")
    else:
        print("No infobox found")

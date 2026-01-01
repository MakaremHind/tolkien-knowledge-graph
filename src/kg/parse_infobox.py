import re

with open("data/elrond.wikitext", encoding="utf-8") as f:
    text = f.read()

pattern = re.compile(
    r"\{\{Infobox character(.*?)\n\}\}",
    re.DOTALL | re.IGNORECASE
)

match = pattern.search(text)
if not match:
    raise ValueError("Infobox character not found")

infobox_text = match.group(1)

with open("data/elrond_infobox.txt", "w", encoding="utf-8") as f:
    f.write(infobox_text)

print("Infobox extracted to data/elrond_infobox.txt")

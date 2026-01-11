import re

WIKI_LINK = re.compile(r"\[\[([^|\]]+)\|?([^\]]*)\]\]")
REF = re.compile(r"<ref[^>]*>.*?</ref>")
HTML = re.compile(r"<[^>]+>")
TEMPLATE = re.compile(r"\{\{[^}]+\}\}")
BOLD_ITALIC = re.compile(r"'''+|''")

def clean_literal(text: str) -> str:
    if not text:
        return text

    # [[Page|Label]] → Label, [[Page]] → Page
    def repl(match):
        return match.group(2) if match.group(2) else match.group(1)

    text = WIKI_LINK.sub(repl, text)
    text = REF.sub("", text)
    text = TEMPLATE.sub("", text)
    text = HTML.sub(" ", text)
    text = BOLD_ITALIC.sub("", text)

    text = re.sub(r"\s+", " ", text)
    return text.strip(" ,.;")

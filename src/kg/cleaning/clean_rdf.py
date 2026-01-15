from pathlib import Path
from clean_literal import clean_literal

SRC = Path("data/knowledge_graph_raw.ttl")
DST = Path("data/knowledge_graph_clean.ttl")

with SRC.open(encoding="utf-8") as fin, DST.open("w", encoding="utf-8") as fout:
    for line in fin:
        # Only clean lines with literals
        if '"' in line:
            try:
                prefix, rest = line.split('"', 1)
                literal, suffix = rest.rsplit('"', 1)
                literal = clean_literal(literal)
                line = f'{prefix}"{literal}"{suffix}'
            except ValueError:
                pass  # leave line unchanged if parsing fails

        fout.write(line)

print("✔ Clean RDF written to data/knowledge_graph_clean.ttl")

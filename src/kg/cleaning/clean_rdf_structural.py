from pathlib import Path
import re

SRC = Path("data/knowledge_graph_clean.ttl")
DST = Path("data/knowledge_graph_final.ttl")

PLACEHOLDERS = {
    "see below",
    "See cast section below for more",
    ""
}

def is_bad_literal(value: str) -> bool:
    return value.strip() in PLACEHOLDERS

with SRC.open(encoding="utf-8") as fin, DST.open("w", encoding="utf-8") as fout:
    seen = set()

    for line in fin:
        line = line.rstrip()

        # Remove empty literals
        if '""' in line:
            continue

        # Remove placeholders
        if '"' in line:
            try:
                value = line.split('"')[1]
                if is_bad_literal(value):
                    continue
            except IndexError:
                pass

        # Remove duplicate predicates per subject
        if line.startswith("ex:"):
            seen.clear()

        if ";" in line and "schema:" in line:
            predicate = line.split("schema:")[1].split()[0]
            if predicate in seen:
                continue
            seen.add(predicate)

        fout.write(line + "\n")

print("✔ Final RDF written to data/knowledge_graph_final.ttl")

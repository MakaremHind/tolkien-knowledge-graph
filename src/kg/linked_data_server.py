from __future__ import annotations

from flask import Flask, request, Response, redirect
import requests
from rdflib import Graph, URIRef, Literal
from urllib.parse import quote, unquote
import html

# =========================
# Config
# =========================

FUSEKI_QUERY_URL = "http://localhost:3030/tolkien/query"   # this is the endpoint you used successfully
FUSEKI_SPARQL_URL = "http://localhost:3030/tolkien/sparql" # optional fallback (sometimes enabled)
ENTITY_BASE = "http://example.org/tolkien/"

app = Flask(__name__)

# NOTE:
# We do NOT use .format() with SPARQL braces anymore to avoid KeyError.
# We use a placeholder token and .replace().
CONSTRUCT_DESCRIPTION = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>

CONSTRUCT {
  ?s ?p ?o .
}
WHERE {
  VALUES ?focus { <__ENTITY__> }

  {
    SELECT DISTINCT ?x WHERE {
      VALUES ?focus { <__ENTITY__> }
      { BIND(?focus AS ?x) }
      UNION { ?focus owl:sameAs ?x }
      UNION { ?x owl:sameAs ?focus }
    }
  }

  { ?x ?p ?o . BIND(?x AS ?s) }
  UNION
  { ?s ?p ?x . BIND(?x AS ?o) }
}
"""

# =========================
# Fuseki access
# =========================

def fuseki_construct(entity_uri: str) -> str:
    """
    Send a CONSTRUCT query to Fuseki and return Turtle (string).
    """
    sparql = CONSTRUCT_DESCRIPTION.replace("__ENTITY__", entity_uri)

    # Try /query first, then fallback to /sparql if needed.
    for endpoint in (FUSEKI_QUERY_URL, FUSEKI_SPARQL_URL):
        try:
            r = requests.post(
                endpoint,
                data={"query": sparql},
                headers={"Accept": "text/turtle"},
                timeout=30,
            )
            if r.status_code == 200 and r.text.strip():
                return r.text
        except requests.RequestException:
            pass

    return ""


# =========================
# Content negotiation
# =========================

def prefers_html() -> bool:
    """
    Very simple content negotiation:
    - If client explicitly asks for Turtle, return Turtle.
    - Otherwise return HTML (browsers default to HTML).
    """
    accept = (request.headers.get("Accept") or "").lower()

    if "text/turtle" in accept or "application/x-turtle" in accept:
        return False
    # If someone asks RDF-ish, you can decide to return turtle too.
    if "application/ld+json" in accept or "application/rdf+xml" in accept or "application/n-triples" in accept:
        return False

    return True


# =========================
# HTML rendering
# =========================

def _pick_first_literal(g: Graph, subj: URIRef, preds: list[URIRef]) -> str:
    for p in preds:
        for o in g.objects(subj, p):
            if isinstance(o, Literal):
                return str(o)
            return str(o)
    return ""


def graph_to_html(entity_uri: str, turtle_data: str) -> str:
    g = Graph()
    g.parse(data=turtle_data, format="turtle")

    subj = URIRef(entity_uri)

    # Title
    title = _pick_first_literal(
        g,
        subj,
        [
            URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
            URIRef("https://schema.org/name"),
        ],
    ) or entity_uri

    # Short description
    description = _pick_first_literal(
        g,
        subj,
        [
            URIRef("https://schema.org/description"),
            URIRef("http://purl.org/dc/terms/description"),
        ],
    )

    # Illustration
    image_url = ""
    for pred in (
        URIRef("https://schema.org/image"),
        URIRef("https://schema.org/thumbnailUrl"),
    ):
        for o in g.objects(subj, pred):
            image_url = str(o)
            break
        if image_url:
            break

    # Collect outgoing + incoming direct relations (already sameAs-aware from CONSTRUCT)
    rows: list[tuple[str, str, str]] = []

    # Outgoing: subj ?p ?o
    for p, o in g.predicate_objects(subj):
        rows.append(("out", str(p), str(o)))

    # Incoming: ?s ?p subj
    for s in g.subjects(None, subj):
        for p in g.predicates(s, subj):
            rows.append(("in", str(p), str(s)))

    # Deduplicate rows (Fuseki may return repeats due to sameAs expansion)
    rows = sorted(set(rows), key=lambda x: (x[0], x[1], x[2]))

    def linkify(value: str) -> str:
        # Escape everything by default
        safe = html.escape(value)

        if value.startswith("http://") or value.startswith("https://"):
            # If it's one of our entities, link to our /resource route
            if value.startswith(ENTITY_BASE):
                local = "/resource/" + quote(value[len(ENTITY_BASE):], safe="")
                return f'<a href="{local}">{safe}</a>'
            return f'<a href="{html.escape(value)}">{safe}</a>'

        return safe

    img_html = (
        f'<img src="{html.escape(image_url)}" style="max-width:240px;border-radius:12px;" />'
        if image_url
        else ""
    )
    desc_html = f"<p>{html.escape(description)}</p>" if description else ""

    table_rows = "\n".join(
        f"<tr><td>{html.escape(direction)}</td><td>{linkify(p)}</td><td>{linkify(v)}</td></tr>"
        for direction, p, v in rows
    )

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    .header {{ display: flex; gap: 24px; align-items: flex-start; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 18px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #f6f6f6; }}
    code {{ background:#f2f2f2; padding:2px 4px; border-radius:4px; }}
  </style>
</head>
<body>
  <div class="header">
    <div>
      <h1>{html.escape(title)}</h1>
      <p><code>{html.escape(entity_uri)}</code></p>
      {desc_html}
      <p>
        <a href="/data?uri={quote(entity_uri, safe='')}">Download Turtle</a>
      </p>
    </div>
    <div>{img_html}</div>
  </div>

  <h2>Direct relations (outgoing + incoming, owl:sameAs-aware)</h2>
  <table>
    <tr><th>direction</th><th>predicate</th><th>value</th></tr>
    {table_rows}
  </table>
</body>
</html>
"""


# =========================
# Routes
# =========================

@app.get("/")
def home():
    return redirect("/resource/Elijah_Wood")


@app.get("/resource/<path:local_name>")
def resource(local_name: str):
    local_name = unquote(local_name)
    entity_uri = ENTITY_BASE + local_name

    turtle_data = fuseki_construct(entity_uri)
    if not turtle_data:
        return Response(f"Not found or no triples for {entity_uri}\n", status=404, mimetype="text/plain")

    if prefers_html():
        return Response(graph_to_html(entity_uri, turtle_data), mimetype="text/html")
    return Response(turtle_data, mimetype="text/turtle")


@app.get("/data")
def data():
    uri = request.args.get("uri", "")
    if not uri:
        return Response("Missing ?uri=\n", status=400, mimetype="text/plain")

    uri = unquote(uri)
    turtle_data = fuseki_construct(uri)
    if not turtle_data:
        return Response(f"Not found or no triples for {uri}\n", status=404, mimetype="text/plain")

    return Response(turtle_data, mimetype="text/turtle")


# =========================
# Main
# =========================

if __name__ == "__main__":
    print("Linked Data server running at http://localhost:8000")
    print("Example: http://localhost:8000/resource/Elijah_Wood")
    app.run(host="0.0.0.0", port=8000, debug=True)

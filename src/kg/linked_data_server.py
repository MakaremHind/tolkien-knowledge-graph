from __future__ import annotations

from flask import Flask, request, Response, redirect
import requests
from rdflib import Graph, URIRef, Literal
from urllib.parse import quote, unquote
import html

# =========================
# Config
# =========================

FUSEKI_QUERY_URL = "http://localhost:3030/tolkien/query"   # works with your UI
FUSEKI_SPARQL_URL = "http://localhost:3030/tolkien/sparql" # optional fallback
ENTITY_BASE = "http://example.org/tolkien/"

app = Flask(__name__)

# =========================
# SPARQL queries
# =========================

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

LIST_ENTITIES = """
PREFIX schema: <https://schema.org/>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?s ?label
WHERE {
  ?s a ?type .
  FILTER(STRSTARTS(STR(?s), "__ENTITY_BASE__"))

  OPTIONAL { ?s schema:name ?n . }
  OPTIONAL { ?s rdfs:label ?l . }

  BIND(COALESCE(STR(?n), STR(?l), REPLACE(STR(?s), "__ENTITY_BASE__", "")) AS ?label)
}
ORDER BY LCASE(?label)
LIMIT __LIMIT__
"""

SEARCH_ENTITIES = """
PREFIX schema: <https://schema.org/>
PREFIX rdfs:   <http://www.w3.org/2000/01/rdf-schema#>

SELECT DISTINCT ?s ?label
WHERE {
  ?s a ?type .
  FILTER(STRSTARTS(STR(?s), "__ENTITY_BASE__"))

  OPTIONAL { ?s schema:name ?n . }
  OPTIONAL { ?s rdfs:label ?l . }

  BIND(COALESCE(STR(?n), STR(?l), REPLACE(STR(?s), "__ENTITY_BASE__", "")) AS ?label)

  FILTER(CONTAINS(LCASE(?label), LCASE("__Q__")))
}
ORDER BY LCASE(?label)
LIMIT __LIMIT__
"""

# =========================
# Fuseki helpers
# =========================

def _post_sparql_select(query: str) -> dict | None:
    """
    Execute a SELECT query against Fuseki and return JSON dict.
    """
    for endpoint in (FUSEKI_QUERY_URL, FUSEKI_SPARQL_URL):
        try:
            r = requests.post(
                endpoint,
                data={"query": query},
                headers={"Accept": "application/sparql-results+json"},
                timeout=30,
            )
            if r.status_code == 200:
                return r.json()
        except Exception:
            pass
    return None


def fuseki_construct(entity_uri: str) -> str:
    """
    Send a CONSTRUCT query to Fuseki and return Turtle (string).
    """
    sparql = CONSTRUCT_DESCRIPTION.replace("__ENTITY__", entity_uri)

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
    accept = (request.headers.get("Accept") or "").lower()

    if "text/turtle" in accept or "application/x-turtle" in accept:
        return False
    if "application/ld+json" in accept or "application/rdf+xml" in accept or "application/n-triples" in accept:
        return False

    return True


# =========================
# HTML rendering
# =========================

def _pick_first_literal(g: Graph, subj: URIRef, preds: list[URIRef]) -> str:
    for p in preds:
        for o in g.objects(subj, p):
            return str(o)
    return ""


def _linkify(value: str) -> str:
    safe = html.escape(value)

    if value.startswith("http://") or value.startswith("https://"):
        if value.startswith(ENTITY_BASE):
            local = "/resource/" + quote(value[len(ENTITY_BASE):], safe="")
            return f'<a href="{local}">{safe}</a>'
        return f'<a href="{html.escape(value)}">{safe}</a>'

    return safe


def graph_to_html(entity_uri: str, turtle_data: str) -> str:
    g = Graph()
    g.parse(data=turtle_data, format="turtle")

    subj = URIRef(entity_uri)

    title = _pick_first_literal(
        g,
        subj,
        [
            URIRef("http://www.w3.org/2000/01/rdf-schema#label"),
            URIRef("https://schema.org/name"),
        ],
    ) or entity_uri

    description = _pick_first_literal(
        g,
        subj,
        [
            URIRef("https://schema.org/description"),
            URIRef("http://purl.org/dc/terms/description"),
        ],
    )

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

    rows: list[tuple[str, str, str]] = []

    for p, o in g.predicate_objects(subj):
        rows.append(("out", str(p), str(o)))

    for s in g.subjects(None, subj):
        for p in g.predicates(s, subj):
            rows.append(("in", str(p), str(s)))

    rows = sorted(set(rows), key=lambda x: (x[0], x[1], x[2]))

    img_html = (
        f'<img src="{html.escape(image_url)}" style="max-width:240px;border-radius:12px;" />'
        if image_url
        else ""
    )
    desc_html = f"<p>{html.escape(description)}</p>" if description else ""

    table_rows = "\n".join(
        f"<tr><td>{html.escape(direction)}</td><td>{_linkify(p)}</td><td>{_linkify(v)}</td></tr>"
        for direction, p, v in rows
    )

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>{html.escape(title)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    .topbar {{ display:flex; gap:12px; align-items:center; margin-bottom:16px; }}
    .header {{ display: flex; gap: 24px; align-items: flex-start; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 18px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; vertical-align: top; }}
    th {{ background: #f6f6f6; }}
    code {{ background:#f2f2f2; padding:2px 4px; border-radius:4px; }}
    .searchbox input {{ padding:8px; width:320px; }}
    .searchbox button {{ padding:8px 12px; }}
  </style>
</head>
<body>

  <div class="topbar">
    <a href="/">Home</a>
    <form class="searchbox" action="/search" method="get">
      <input type="text" name="q" placeholder="Search entities..." />
      <button type="submit">Search</button>
    </form>
  </div>

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


def render_homepage(limit: int = 200) -> str:
    q = LIST_ENTITIES.replace("__ENTITY_BASE__", ENTITY_BASE).replace("__LIMIT__", str(limit))
    data = _post_sparql_select(q)

    items = []
    if data:
        for b in data.get("results", {}).get("bindings", []):
            uri = b["s"]["value"]
            label = b.get("label", {}).get("value", uri.replace(ENTITY_BASE, ""))
            local = "/resource/" + quote(uri[len(ENTITY_BASE):], safe="")
            items.append((label, local, uri))

    lis = "\n".join(
        f'<li><a href="{html.escape(local)}">{html.escape(label)}</a> '
        f'<small><code>{html.escape(uri)}</code></small></li>'
        for (label, local, uri) in items
    )

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Tolkien KG — Linked Data</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    .topbar {{ display:flex; gap:12px; align-items:center; margin-bottom:16px; }}
    .searchbox input {{ padding:8px; width:320px; }}
    .searchbox button {{ padding:8px 12px; }}
    ul {{ line-height: 1.8; }}
    code {{ background:#f2f2f2; padding:2px 4px; border-radius:4px; }}
  </style>
</head>
<body>
  <div class="topbar">
    <strong>Home</strong>
    <form class="searchbox" action="/search" method="get">
      <input type="text" name="q" placeholder="Search entities..." />
      <button type="submit">Search</button>
    </form>
  </div>

  <h1>Tolkien KG — Linked Data interface</h1>
  <p>Showing up to {limit} entities from <code>{html.escape(ENTITY_BASE)}</code>.</p>

  <ul>
    {lis if lis else "<li><em>No entities found. Did you upload data to Fuseki?</em></li>"}
  </ul>
</body>
</html>
"""


def render_search_page(qtext: str, limit: int = 200) -> str:
    qsafe = qtext.strip()
    sparql = (
        SEARCH_ENTITIES.replace("__ENTITY_BASE__", ENTITY_BASE)
        .replace("__Q__", qsafe.replace('"', '\\"'))
        .replace("__LIMIT__", str(limit))
    )

    data = _post_sparql_select(sparql)

    items = []
    if data:
        for b in data.get("results", {}).get("bindings", []):
            uri = b["s"]["value"]
            label = b.get("label", {}).get("value", uri.replace(ENTITY_BASE, ""))
            local = "/resource/" + quote(uri[len(ENTITY_BASE):], safe="")
            items.append((label, local, uri))

    lis = "\n".join(
        f'<li><a href="{html.escape(local)}">{html.escape(label)}</a> '
        f'<small><code>{html.escape(uri)}</code></small></li>'
        for (label, local, uri) in items
    )

    return f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Search — {html.escape(qsafe)}</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 24px; }}
    .topbar {{ display:flex; gap:12px; align-items:center; margin-bottom:16px; }}
    .searchbox input {{ padding:8px; width:320px; }}
    .searchbox button {{ padding:8px 12px; }}
    ul {{ line-height: 1.8; }}
    code {{ background:#f2f2f2; padding:2px 4px; border-radius:4px; }}
  </style>
</head>
<body>
  <div class="topbar">
    <a href="/">Home</a>
    <form class="searchbox" action="/search" method="get">
      <input type="text" name="q" value="{html.escape(qsafe)}" />
      <button type="submit">Search</button>
    </form>
  </div>

  <h1>Search results</h1>
  <p>Query: <code>{html.escape(qsafe)}</code> — showing up to {limit} matches.</p>

  <ul>
    {lis if lis else "<li><em>No matches found.</em></li>"}
  </ul>
</body>
</html>
"""


# =========================
# Routes
# =========================

@app.get("/")
def home():
    return Response(render_homepage(limit=200), mimetype="text/html")


@app.get("/id/<path:name>")
def id_redirect(name: str):
    # 303 "See Other": best practice for redirecting from identifier to representation
    name = unquote(name)
    return redirect("/resource/" + quote(name, safe=""), code=303)


@app.get("/search")
def search():
    q = (request.args.get("q") or "").strip()
    if not q:
        return Response(render_search_page("", limit=200), mimetype="text/html")
    return Response(render_search_page(q, limit=200), mimetype="text/html")


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
    print("Homepage: http://localhost:8000/")
    print("Example:  http://localhost:8000/resource/Elijah_Wood")
    print("Redirect: http://localhost:8000/id/Elijah_Wood")
    print("Search:   http://localhost:8000/search?q=wood")
    app.run(host="0.0.0.0", port=8000, debug=True)

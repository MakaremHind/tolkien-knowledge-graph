from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS
from infobox_mapping import INFOBOX_TO_RDF, SCHEMA

EX = Namespace("http://example.org/tolkien/")

def character_infobox_to_rdf(page_title: str, infobox: dict) -> Graph:
    """
    Generate an RDF graph for a Tolkien character from its infobox dictionary.
    """
    g = Graph()
    g.bind("schema", SCHEMA)
    g.bind("ex", EX)

    subject = URIRef(EX[page_title.replace(" ", "_")])

    # Basic typing
    g.add((subject, RDF.type, SCHEMA.Person))
    g.add((subject, RDFS.label, Literal(page_title, lang="en")))

    # Link to original wiki page
    g.add((
        subject,
        SCHEMA.sameAs,
        URIRef(f"https://tolkiengateway.net/wiki/{page_title.replace(' ', '_')}")
    ))

    # Process infobox fields
    for field, value in infobox.items():
        if field not in INFOBOX_TO_RDF:
            continue

        predicate = INFOBOX_TO_RDF[field]

        # Simple cleanup (we improve this later)
        clean_value = (
            value.replace("[[", "")
                 .replace("]]", "")
                 .replace("<br/>", ", ")
                 .strip()
        )

        if clean_value:
            g.add((subject, predicate, Literal(clean_value)))

    return g

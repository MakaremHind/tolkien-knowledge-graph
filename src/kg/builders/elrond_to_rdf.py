from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS

# Namespaces
SCHEMA = Namespace("https://schema.org/")
EX = Namespace("http://example.org/tolkien/")

# Create graph
g = Graph()
g.bind("schema", SCHEMA)
g.bind("ex", EX)

# Elrond entity
elrond = URIRef(EX["Elrond"])

g.add((elrond, RDF.type, SCHEMA.Person))
g.add((elrond, RDFS.label, Literal("Elrond", lang="en")))
g.add((elrond, SCHEMA.name, Literal("Elrond")))

# Infobox values (hard-coded for this first example)
g.add((elrond, SCHEMA.jobTitle, Literal("Lord of Rivendell")))
g.add((elrond, SCHEMA.species, Literal("Half-elf")))
g.add((elrond, SCHEMA.location, Literal("Rivendell")))

# Link to original wiki page
g.add((
    elrond,
    SCHEMA.sameAs,
    URIRef("https://tolkiengateway.net/wiki/Elrond")
))

# Serialize
g.serialize(destination="data/elrond.ttl", format="turtle")

print("RDF graph written to data/elrond.ttl")

from pyshacl import validate
from rdflib import Graph

# =========================
# Load RDF data graph
# =========================
data_graph = Graph()
data_graph.parse(
    "data/knowledge_graph_raw.ttl",
    format="turtle"
)

# =========================
# Load SHACL shapes graph
# =========================
shapes_graph = Graph()
shapes_graph.parse(
    "SHACL/tolkien_shapes.ttl",
    format="turtle"
)

# =========================
# Run SHACL validation
# =========================
conforms, report_graph, report_text = validate(
    data_graph=data_graph,
    shacl_graph=shapes_graph,
    inference="rdfs",
    debug=True
)

# =========================
# Print results
# =========================
print("SHACL Conforms:", conforms)
print("------ Validation Report ------")
print(report_text)

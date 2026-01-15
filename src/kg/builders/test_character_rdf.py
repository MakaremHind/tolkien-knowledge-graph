from infobox_to_dict import load_infobox_dict
from character_to_rdf import character_infobox_to_rdf

infobox = load_infobox_dict("data/elrond_infobox.txt")
graph = character_infobox_to_rdf("Elrond", infobox)

graph.serialize(destination="data/elrond.ttl", format="turtle")
print("Elrond RDF regenerated via generic procedure")

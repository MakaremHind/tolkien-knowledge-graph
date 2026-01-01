from rdflib import Namespace

SCHEMA = Namespace("https://schema.org/")

INFOBOX_TO_RDF = {
    "name": SCHEMA.name,
    "titles": SCHEMA.jobTitle,
    "people": SCHEMA.species,
    "race": SCHEMA.species,
    "gender": SCHEMA.gender,
    "location": SCHEMA.location,
    "affiliation": SCHEMA.memberOf,
}

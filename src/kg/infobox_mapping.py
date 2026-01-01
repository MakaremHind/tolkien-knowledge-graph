from rdflib import Namespace

SCHEMA = Namespace("https://schema.org/")

FIELD_MAPPING = {
    "name": SCHEMA.name,
    "titles": SCHEMA.jobTitle,
    "people": SCHEMA.species,
    "race": SCHEMA.species,
    "gender": SCHEMA.gender,
    "location": SCHEMA.location,
    "affiliation": SCHEMA.memberOf,
}

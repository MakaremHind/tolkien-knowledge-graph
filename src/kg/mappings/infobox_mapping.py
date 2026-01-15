from rdflib import Namespace

SCHEMA = Namespace("https://schema.org/")

FIELD_MAPPING = {
    "titles": "schema:jobTitle",
    "people": "schema:species",
    "race": "schema:species",
    "gender": "schema:gender",
    "location": "schema:location",
    "affiliation": "schema:memberOf",
}


from rdflib import Namespace

SCHEMA = Namespace("https://schema.org/")

FIELD_MAPPING = {
    "played": "schema:characterName",
    "played2": "schema:characterName",
    "played3": "schema:characterName",
    "film": "schema:workPerformedIn",
    "film2": "schema:workPerformedIn",
    "film3": "schema:workPerformedIn",
    "lifetime": "schema:description",
}


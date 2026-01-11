from rdflib import Namespace

SCHEMA = Namespace("https://schema.org/")

FIELD_MAPPING = {
    "born": "schema:birthDate",
    "died": "schema:deathDate",
    "education": "schema:alumniOf",
    "occupation": "schema:occupation",
    "location": "schema:location",
    "website": "schema:sameAs",
}

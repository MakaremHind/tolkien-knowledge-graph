from rdflib import Namespace

SCHEMA = Namespace("https://schema.org/")

FIELD_MAPPING = {
    "name": "schema:name",
    "othernames": "schema:alternateName",
    "founded": "schema:foundingDate",
    "founder": "schema:founder",
    "purpose": "schema:description",
    "members": "schema:member",
    "location": "schema:location",
    "disbanded": "schema:dissolutionDate",
    "notablefor": "schema:knowsAbout",
}

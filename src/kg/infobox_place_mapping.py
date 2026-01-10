from rdflib import Namespace

SCHEMA = Namespace("https://schema.org/")

FIELD_MAPPING = {
    "type": "schema:additionalType",
    "location": "schema:containedInPlace",
    "regions": "schema:containedInPlace",
    "settlements": "schema:containsPlace",
    "inhabitants": "schema:population",
    "created": "schema:dateCreated",
    "destroyed": "schema:dateDeleted",
    "description": "schema:description",
}

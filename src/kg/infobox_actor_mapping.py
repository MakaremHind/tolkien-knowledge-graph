from rdflib import Namespace

SCHEMA = Namespace("https://schema.org/")

FIELD_MAPPING = {
    "name": SCHEMA.name,
    "played": SCHEMA.characterName,
    "played2": SCHEMA.characterName,
    "played3": SCHEMA.characterName,
    "film": SCHEMA.workPerformedIn,
    "film2": SCHEMA.workPerformedIn,
    "film3": SCHEMA.workPerformedIn,
    "imdb": SCHEMA.sameAs,
    "lifetime": SCHEMA.description
}

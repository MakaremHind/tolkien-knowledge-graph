from rdflib import Namespace

SCHEMA = Namespace("https://schema.org/")

FIELD_MAPPING = {
    "director": "schema:director",
    "writer": "schema:author",
    "screenplay": "schema:author",
    "basedon": "schema:isBasedOn",
    "producer": "schema:producer",
    "starring": "schema:actor",
    "narrator": "schema:narrator",
    "cinematography": "schema:cinematography",
    "editing": "schema:editor",
    "music": "schema:musicBy",
    "animator": "schema:animator",
    "production design": "schema:productionDesign",
    "studio": "schema:productionCompany",
    "distributor": "schema:distributor",
    "released": "schema:datePublished",
    "runtime": "schema:duration",
    "country": "schema:countryOfOrigin",
    "language": "schema:inLanguage",
    "budget": "schema:budget",
    "gross": "schema:gross",
}

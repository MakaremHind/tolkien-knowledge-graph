from rdflib import Namespace

SCHEMA = Namespace("https://schema.org/")

FIELD_MAPPING = {
    "title": "schema:name",
    "author": "schema:author",
    "editor": "schema:editor",
    "translator": "schema:translator",
    "illustrator": "schema:illustrator",
    "genre": "schema:genre",
    "subject": "schema:about",
    "publisher": "schema:publisher",
    "date": "schema:datePublished",
    "dateUK": "schema:datePublished",
    "dateUS": "schema:datePublished",
    "pages": "schema:numberOfPages",
    "isbn": "schema:isbn",
    "isbn2": "schema:isbn",
    "series": "schema:isPartOfSeries",
    "precededby": "schema:isBasedOn",
    "followedby": "schema:hasPart",
}

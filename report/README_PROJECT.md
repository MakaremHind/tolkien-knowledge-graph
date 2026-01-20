# Tolkien Knowledge Graph – Project Narrative

This README documents **what was implemented and why**, following the assignment tasks from the first commit up to the current state of the repository.

> Repository structure
- `data/` – raw inputs (exported wiki outputs, lists) + generated RDF TTL outputs
- `src/kg/` – Python scripts that fetch/parse wikitext and generate RDF
- `fuseki/` – Fuseki dataset folder (local triplestore storage)
- `ontology/` – ontology/vocabulary file(s) (`tolkien_ontology.ttl`)
- `SHACL/` – SHACL shapes + validation script
- `sparql/` – SPARQL queries (created for the last task)


## 1) Triplestore setup (Fuseki)

We set up Apache Jena Fuseki as a local triplestore to store and query the generated RDF.  
The repository contains a `fuseki/` folder to keep dataset-related files.

**Goal:** have a SPARQL endpoint to load TTL outputs and query them.


## 2) First RDF generation from one example page (Elrond)

We started with one concrete page (`Elrond`) and:
1. retrieved page source in **wikitext** (“View source” on Tolkien Gateway)
2. extracted the **infobox template** call (e.g., `{{infobox character | ... }}`)
3. parsed the infobox with a Python procedure
4. generated an RDF graph encoding the infobox fields as RDF triples

**Artifacts produced**
- `data/elrond.wikitext` – raw wiki source (or fetched snapshot)
- `data/elrond_infobox.txt` – extracted infobox template text
- `data/elrond.ttl` – RDF produced for Elrond


## 3) Procedure to generate RDF for many character infoboxes

After validating the Elrond proof-of-concept, we generalized:
- a pipeline to take a list of character pages (Third Age characters)
- fetch their wikitext using the MediaWiki API
- parse each character infobox
- write RDF TTL for each (or a merged graph)

**Key implementation points**
- We used `action=query` (category members) and/or stored text files with lists.
- We wrote scripts to fetch pages and transform infoboxes into RDF consistently.

**Artifacts produced**
- `data/third_age_characters.txt`
- `data/characters.ttl` (or character-related TTL outputs)


## 4) Repeat for more infobox types

We extended the infobox parsing/mapping approach to multiple types:
- people / actors
- authors
- books
- films
- organizations
- places

This resulted in multiple mapping scripts and generators under `src/kg/`, such as:
- `actor_to_rdf.py`, `author_to_rdf.py`, `book_to_rdf.py`, `film_to_rdf.py`
- `organization_to_rdf.py`, `place_to_rdf.py`
- “infobox mapping” helpers for each infobox type (`infobox_*_mapping.py`)

**Output growth**
- merged outputs: `knowledge_graph.ttl`, then cleaned/final versions
  - `knowledge_graph_raw.ttl`
  - `knowledge_graph_clean.ttl`
  - `knowledge_graph_final.ttl`


## 5) Exhaustive page listing (allpages) and page/resource distinction

We used the MediaWiki API to list pages using:
- `action=query&list=allpages` with pagination (`continue` token)

Then we generated a DBpedia/YAGO-style distinction between:
- a **wiki page** URI
- a **resource/entity** URI

The graph includes triples stating that a page is “about” an entity, and that the entity is distinct but shares a label/name.

This supports later integration/alignment tasks and follows best practices from DBpedia:
- `/page/X` is not the same as `/resource/X`, but page *is about* the resource.

(Exact predicate depends on your modeling choice; commonly `schema:about` or `foaf:primaryTopic`.)


## 6) Vocabulary / Ontology aligned to schema.org

We created a vocabulary (RDFS/OWL-ish) to represent Tolkien Gateway information, aligned to schema.org.
This lives in:
- `ontology/tolkien_ontology.ttl`

We chose to **keep RDF instances typed as schema.org classes** (e.g., `schema:Person`, `schema:Book`, `schema:Movie`, `schema:Organization`) and treat our ontology classes as the conceptual model.

In Protégé, we aligned / connected ontology classes to schema.org where appropriate (class equivalences/subclasses).


## 7) SHACL shapes based on infobox templates

We translated infobox constraints into SHACL NodeShapes so that each class is covered by at least one shape.
Shapes are stored in:
- `SHACL/tolkien_shapes.ttl`

Validation script:
- `SHACL/validate_shacl.py`


## 8) External alignment to Wikipedia → DBpedia and YAGO

Task:
> Use the MediaWiki API to retrieve Tolkien Gateway links to Wikipedia (parse action with parameter `prop=externallinks`). Find alignments with DBpedia and YAGO by looking for resources that link to the same Wikipedia pages.

Implementation:
- script: `src/kg/align_external_kgs.py`
- input graph: `data/knowledge_graph_final.ttl`
- output graph: `data/alignment_external.ttl`

Main idea:
1. for each entity with `schema:sameAs` pointing to Tolkien Gateway (`tolkiengateway.net/wiki/...`)
2. fetch external links for that Tolkien Gateway page:
   - `action=parse&page=<Title>&prop=externallinks&format=json`
3. filter Wikipedia links (`wikipedia.org/wiki/...`)
4. create alignment triples:
   - `owl:sameAs` to the Wikipedia URL
   - `owl:sameAs` to derived DBpedia resource URI
   - `owl:sameAs` to derived YAGO resource URI

Debugging outcome:
- We initially got 0 results because Wikipedia requests were returning `403` or the JSON parsing was failing.
- We fixed it by using a safer Wikipedia existence check via the Wikipedia API + proper headers/JSON handling.
- Final run wrote alignments for the subset of entities that actually have Wikipedia pages.

**Artifact produced**
- `data/alignment_external.ttl`


## 9) SPARQL queries without reasoning

Fuseki provides SPARQL, but not RDFS/OWL reasoning by default.
The assignment asks for queries that *simulate* reasoning with property paths and `owl:sameAs` expansion.

We create two queries:
1. **All classes of an entity**, including superclasses (via `rdfs:subClassOf*` property path)
2. **All relations (incoming/outgoing)** for an entity, taking `owl:sameAs` into account

These queries live in `sparql/` and can be executed in Fuseki UI or via curl.

## 10) Linked Data interface (Fuseki + Flask)

This part of the project turns the triples stored in **Apache Jena Fuseki** into a small **Linked Data interface**.

It supports **URI dereferencing** (GET) with **content negotiation**:
- Browsers (Accept: `text/html`) receive an **HTML page**
- RDF clients (Accept: `text/turtle`) receive **Turtle**

It also takes `owl:sameAs` into account: when an entity is aligned to Wikipedia/DBpedia/YAGO, the interface shows direct relations for the entity **and** its `owl:sameAs` equivalents.


## What we implemented

### 1) SameAs-aware “description” query (direct relations)
The server issues a SPARQL `CONSTRUCT` query to Fuseki that returns a *description graph* for a focus entity:

- All outgoing triples: `?x ?p ?o`
- All incoming triples: `?s ?p ?x`
- Where `?x` is the focus entity **or any resource linked by `owl:sameAs` in either direction**

This makes the output “sameAs-aware” without enabling reasoning inside Fuseki.

### 2) HTML view for entities
For an entity, the HTML page shows:
- **Title** (from `rdfs:label` or `schema:name`)
- **Short description** (from `schema:description` or `dcterms:description`)
- **Illustration** if available (`schema:image` or `schema:thumbnailUrl`)
- A table of **direct relations** (outgoing + incoming) with hyperlinks

### 3) Turtle view for entities
If the client requests Turtle, the server returns the Turtle produced by Fuseki’s `CONSTRUCT`.

### 4) Convenience web features
- `/` home page listing entities (up to 200) with links
- `/search?q=...` search page (matches `schema:name` / `rdfs:label`)
- `/id/<name>` **303 redirect** to `/resource/<name>` (Linked Data pattern)
- `/data?uri=<full-uri>` endpoint to download Turtle for any URI


## Files added/updated
- `src/kg/linked_data_server.py` — Flask app implementing the Linked Data interface
- `sparql/` — SPARQL query files used in the previous task (entity classes, relations w/ sameAs, etc.)



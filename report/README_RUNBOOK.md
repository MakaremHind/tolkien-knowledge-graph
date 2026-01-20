# Tolkien Knowledge Graph – Runbook (How to run everything)

This README is a **step-by-step execution guide** for reproducing the pipeline from the first task to the last task, including installations, scripts, commands, and expected outputs.

> OS note: examples use Windows PowerShell paths.


## 0) Prerequisites

### 0.1 Install Python
- Python 3.10+ recommended
- Verify:
```bash
python --version
```

### 0.2 Create and activate a virtual environment (recommended)
```bash
python -m venv .venv
# PowerShell:
.\.venv\Scripts\Activate.ps1
```

### 0.3 Install Python dependencies
run:

```bash
pip install rdflib requests pyshacl beautifulsoup4 lxml
```

Expected result: packages install successfully.


## 1) Task: Set up a triplestore (Fuseki)

### 1.1 Install Apache Jena Fuseki
- Download Apache Jena Fuseki from the official Apache Jena site
- Unzip it somewhere locally

### 1.2 Run Fuseki
From the Fuseki directory:
```bash
java -jar fuseki-server.jar
```
(or the provided `fuseki-server` script depending on distribution)

Expected result:
- Fuseki starts locally, typically at `http://localhost:3030/`

### 1.3 Create a dataset (via UI)
1. Open `http://localhost:3030/`
2. “Manage Datasets” → “Add new dataset”
3. Choose a name (e.g., `tolkien`)

Expected result:
- You have a SPARQL endpoint like:
  - `http://localhost:3030/tolkien/sparql`
  - and an upload UI


## 2) Task: Generate RDF from Elrond infobox (example)

### 2.1 Fetch Elrond wikitext (if script exists)
run
```bash
python src/kg/fetch_elrond_wikitext.py
```

Expected outputs (in `data/`):
- `elrond.wikitext` (or similar raw file)

### 2.2 Parse Elrond infobox + generate RDF
run
```bash
python src/kg/elrond_to_rdf.py
```

Expected outputs:
- `data/elrond_infobox.txt`
- `data/elrond.ttl`


## 3) Task: Generate RDF for Third Age characters

### 3.1 Get the list of third age characters
run
```bash
python src/kg/get_third_age_characters.py
```

Expected output:
- `data/third_age_characters.txt`

### 3.2 Build character KG
run
```bash
python src/kg/build_character_kg.py
```

Expected output:
- `data/characters.ttl` (or character triples merged into a KG file)


## 4) Task: Repeat for more infobox types

Run the generators you have in `src/kg/`.

Typical scripts:
```bash
python src/kg/actor_to_rdf.py
python src/kg/author_to_rdf.py
python src/kg/book_to_rdf.py
python src/kg/film_to_rdf.py
python src/kg/organization_to_rdf.py
python src/kg/place_to_rdf.py
```

Expected outputs:
- `data/actors.ttl` / `data/books.ttl` / `data/films.ttl` / ...
- or a merged `data/knowledge_graph.ttl`


## 5) Task: Build a merged KG + cleanup/final

run
```bash
python src/kg/build_kg.py
```

Expected outputs:
- `data/knowledge_graph.ttl` (merged)

run cleanup scripts:
```bash
python src/kg/clean_rdf_structural.py
python src/kg/clean_rdf.py
python src/kg/clean_literal.py
```

Expected outputs:
- `data/knowledge_graph_clean.ttl`
- `data/knowledge_graph_final.ttl`


## 6) Load data into Fuseki

### 6.1 Upload TTL files via UI
In Fuseki UI (dataset page), upload:
- `data/knowledge_graph_final.ttl`
- optionally `data/alignment_external.ttl`
- optionally `ontology/tolkien_ontology.ttl`

Expected result:
- dataset contains all triples and is queryable


## 7) Task: SHACL shapes + validation

### 7.1 Validate RDF graph with SHACL
Run:
```bash
python SHACL/validate_shacl.py
```

Expected result:
- Terminal prints a validation report
- If `Conforms: True`, the KG satisfies the shapes
- If `Conforms: False`, it prints constraint violations for debugging


## 8) Task: External alignments (Wikipedia/DBpedia/YAGO)

Run:
```bash
python src/kg/align_external_kgs.py
```

Expected output:
- `data/alignment_external.ttl` should be created / updated
- Terminal shows a summary with “Alignments written: <N>” (non-zero once working)


## 9) Task: SPARQL queries (no reasoning)

Create files under `sparql/`:
- `sparql/entity_classes_with_superclasses.rq`
- `sparql/entity_relations_with_sameas.rq`

Then run them in one of these ways:

### Option A: Run in Fuseki Web UI
1. Open dataset → “Query” page
2. Paste query text
3. Run

### Option B: Run via curl (example)
```bash
curl -G "http://localhost:3030/tolkien/sparql"   --data-urlencode "query@sparql/entity_classes_with_superclasses.rq"   -H "Accept: text/csv"
```

Expected result:
- Query 1 returns classes + their superclasses
- Query 2 returns outgoing/incoming relations including sameAs-expanded equivalents


---

# Expected “final state” checklist

You should end up with:

- `data/knowledge_graph_final.ttl` (main KG)
- `ontology/tolkien_ontology.ttl` (schema-aligned vocabulary)
- `SHACL/tolkien_shapes.ttl` + `SHACL/validate_shacl.py` (constraints + validator)
- `data/alignment_external.ttl` + `src/kg/align_external_kgs.py` (external alignment)
- `sparql/*.rq` (SPARQL queries to simulate reasoning + sameAs expansion)
- Fuseki dataset containing TTL uploads and answering SPARQL queries

## 10) Task: SPARQL queries (no reasoning) Linked Data interface (Windows + Fuseki + Flask)

This runbook explains **exactly** how to run the Linked Data interface end-to-end:
1) start Fuseki
2) create a dataset with update enabled
3) upload TTL files into Fuseki
4) run the Flask Linked Data server
5) test the interface (browser + curl)

---

## 10-0) Prerequisites

### Install Java
Fuseki requires Java. Check:

```powershell
java -version
```

### Download Apache Jena Fuseki
Download and extract Fuseki (example folder):

`apache-jena-fuseki-5.6.0`

### Python packages
From the repository root:

install the minimum:

```powershell
python -m pip install flask requests rdflib
```

---

## 10-1) Start Fuseki with a persistent TDB2 dataset

Open **PowerShell** and go to your Fuseki folder:

```powershell
cd C:\Users\HindM\Documents\apache-jena-fuseki-5.6.0
```

Create a DB folder (only needed the first time):

```powershell
mkdir run\databases\tolkien -Force | Out-Null
```

Start Fuseki with:
- **TDB2 storage** (`--tdb2`)
- **persistent location** (`--loc=...`)
- **update enabled** (`--update`) so you can upload data
- dataset name `/tolkien`

```powershell
.\fuseki-server.bat --tdb2 --loc=run\databases\tolkien --update /tolkien
```

Now open the UI:

- http://localhost:3030/

You should see the dataset **/tolkien**.

---

## 10-2) Upload your TTL files to Fuseki

From the **project root** (tolkien-knowledge-graph), run:

```powershell
curl.exe -X POST -H "Content-Type: text/turtle" --data-binary "@data/knowledge_graph_final.ttl" http://localhost:3030/tolkien/data
curl.exe -X POST -H "Content-Type: text/turtle" --data-binary "@data/alignment_external.ttl" http://localhost:3030/tolkien/data
curl.exe -X POST -H "Content-Type: text/turtle" --data-binary "@ontology/tolkien_ontology.ttl" http://localhost:3030/tolkien/data
```

### Expected results
Each command returns JSON like:

```json
{ "count": 296, "tripleCount": 296, "quadCount": 0 }
```

---

## 10-3) Verify that data is loaded

Open Fuseki query UI for your dataset:

- http://localhost:3030/#/dataset/tolkien/query

Run:

```sparql
SELECT (COUNT(*) AS ?triples)
WHERE { ?s ?p ?o }
```

You should see a non-zero triple count.

---

## 10-4) Run the Linked Data server

From the repository root:

```powershell
python src/kg/linked_data_server.py
```

Expected console output:

- `Linked Data server running at http://localhost:8000`
- `Example: http://localhost:8000/resource/Elijah_Wood`

---

## 10-5) Use the interface

### A) Browser (HTML)
- Home (entity listing): http://localhost:8000/
- Entity page: http://localhost:8000/resource/Elijah_Wood
- Search: http://localhost:8000/search?q=elijah

### B) Linked Data redirect pattern (303)
- http://localhost:8000/id/Elijah_Wood  
  → redirects to `/resource/Elijah_Wood`

### C) Turtle output (content negotiation)

Using curl:

```powershell
curl.exe -H "Accept: text/turtle" http://localhost:8000/resource/Elijah_Wood
```

### D) Download Turtle explicitly
- http://localhost:8000/data?uri=http%3A%2F%2Fexample.org%2Ftolkien%2FElijah_Wood

---
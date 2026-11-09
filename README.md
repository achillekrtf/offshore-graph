# Who structures the offshore network of the Panama Papers?

Graph Analytics 2026 project (MSA-DAT07-05, Gianluca Quercini). Authors: Achille Krotoff, Jad Yousri, Adrian Ravas (group of 3, exception to the usual limit of 2, approved by the course).

- **Software:** Python 3.12, NetworkX 3.3, pandas, scipy, python-louvain. Neo4j (local) only for an optional dashboard of the centrality rankings.
- **Report:** [`report/report.pdf`](report/report.pdf) (source: [`report/report.md`](report/report.md))
- **Oral slides:** sources and speaker notes in [`slides/`](slides/)

## Question

**Who structures the offshore network of the Panama Papers?** We identify the central intermediaries, officers and jurisdictions (degree, betweenness, PageRank), then check whether the communities found by Louvain follow the jurisdictions of the entities, the countries of the officers, or the intermediaries.

## Data

Source: ICIJ Offshore Leaks Database, bulk CSV (`full-oldb.LATEST.zip`, generated 2026-09-09, about 72 MB zipped and 1.2 GB unzipped): https://offshoreleaks.icij.org/pages/database

The data is too large for this repository, so it is downloaded from the ICIJ link above into `data/raw/` (ignored by git). The commands are in the next section.

License: the database is under the Open Database License (ODbL 1.0) and its contents under Creative Commons Attribution-ShareAlike 3.0. ICIJ asks users to cite the International Consortium of Investigative Journalists.
Citation: International Consortium of Investigative Journalists (ICIJ), *Offshore Leaks Database*, https://offshoreleaks.icij.org, downloaded 2026-11-06.

Subset used: rows with `sourceID == "Panama Papers"`: 213,634 entities, 238,402 officers, 14,110 intermediaries, 93,454 addresses.

## Reproduce

```bash
# 1. Environment
uv venv --python 3.12 .venv
uv pip install --python .venv/bin/python -r requirements-lock.txt

# 2. Data (about 1.2 GB unzipped)
mkdir -p data/raw
curl -L -o data/full-oldb.zip https://offshoreleaks-data.icij.org/offshoreleaks/csv/full-oldb.LATEST.zip
unzip data/full-oldb.zip -d data/raw

# 3. Build the graphs, write statistics (data/processed/graphs.pkl, stats.json)
.venv/bin/python -I src/run_stats.py

# 4. Diameter and radius (about 2 minutes), writes data/processed/diameter.json
.venv/bin/python -I src/diameter.py

# 5. Sensitivity of the intermediary cap (optional), writes data/processed/cap_sensitivity.json
.venv/bin/python -I src/cap_sensitivity.py
```

Then run the notebooks in order with the Jupyter kernel of `.venv`: `notebooks/01` to `04` (see below). The report PDF is rebuilt with `uv run --no-project --with markdown python report/build_pdf.py` (needs Google Chrome).

**Neo4j (optional).** `src/import_neo4j.py` loads the same data into a local Neo4j, and section 6 of notebook 03 reads from it and writes the rankings back for the dashboard in `neo4j/`. It needs a local Neo4j instance and credentials in the environment variables `NEO4J_URI`, `NEO4J_USERNAME`, `NEO4J_PASSWORD`, `NEO4J_DATABASE`. All other results are computed in NetworkX and do not need Neo4j.

## Repository structure

```
src/        load.py (CSV filter, cache), graph.py (bipartite graph, projection, statistics),
            run_stats.py, diameter.py (exact and bounded diameter and radius),
            cap_sensitivity.py, import_neo4j.py (optional)
notebooks/  01_data_and_graph, 02_connectivity, 03_centralities, 04_communities
figures/    figures used in the report and the slides
report/     report.md, report.pdf, build_pdf.py
slides/     oral defense slides (sources, speaker notes, timing)
neo4j/      centrality dashboard and Cypher queries (optional)
data/       raw and processed data (ignored by git)
```

## Notebooks

| Notebook | Content |
|---|---|
| `01_data_and_graph` | Raw files, filter, bipartite graph, projection, basic statistics |
| `02_connectivity` | Components, exact diameter and radius (projection), bounds (bipartite) |
| `03_centralities` | Degree, PageRank, sampled betweenness, jurisdictions |
| `04_communities` | Louvain, stability, comparison with jurisdiction, officer country and intermediary |

## Graph model

- **Bipartite graph:** entities on one side, connectors (officers, intermediaries, entity addresses) on the other. Undirected, simple, unweighted.
- **Entity projection:** two entities are linked if they share a connector, weight = number of shared connectors. A connector linked to `d` entities adds `d(d-1)/2` edges, so hubs are ignored in the projection: officers with more than 500 entities, intermediaries and addresses with more than 50.
- `registered_address` links go mostly from an officer to an address (145,795 of 151,105), so addresses add little to the entity projection.

## Main results

| | Bipartite | Entity projection |
|---|---|---|
| Nodes | 468,623 | 213,634 |
| Edges | 511,687 | 1,238,967 |
| Components | 12,218 | 139,643 (129,607 isolated) |
| Largest component | 310,904 (66.3 %) | 26,643 (12.5 %) |
| Diameter, radius (giant component) | at least 37, at most 20 (bounds) | 30, 16 (exact) |

- Centralities: a few intermediaries (Orion House Services with 7,016 entities, Mossack Fonseca offices) and one nominee officer carry the network.
- Communities: Louvain gives 158 communities on the giant component (modularity 0.957). They follow the intermediaries (NMI 0.77) more than the countries of the officers (0.43) and far more than the jurisdictions (0.13).

## Reuse and AI tools

- **Existing code for this dataset:** none reused. Apart from the libraries above and the algorithms cited in the report, all code was written by the group.
- **AI tools:** Claude Code and Cursor, used by the three authors for coding help, debugging and drafting. Details are in section 9 of the report.

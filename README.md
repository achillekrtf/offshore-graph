# Offshore network analysis (Graph Analytics project 2026)

Course: MSA-DAT07-05 Graph Analytics (Gianluca Quercini). Group of 3 (exception to the usual limit of 2, approved by the course): Achille Krotoff, Jad Yousri, Adrian Ravas.

- **Report deadline:** 10 November 2026, 8:00 AM (PDF, 15 pages max, template on Inside)
- **Oral defense:** 10 November 2026, between 2:00 PM and 5:00 PM (8 min talk + 2 min questions, both students speak)
- **Software:** NetworkX (Python)

## Question

Who structures the offshore network? Compare central intermediaries and jurisdictions (degree, betweenness, PageRank) with the communities found by Louvain, and check whether communities follow jurisdictions or the leak of origin (Panama, Paradise, Pandora Papers).

## Data

ICIJ Offshore Leaks Database (CSV bulk download): https://offshoreleaks.icij.org/pages/database
Version used: bulk CSV generated 2026-09-09 (`full-oldb.LATEST.zip`, 72 MB zipped).
Subset: **Panama Papers** only (`sourceID == "Panama Papers"`): 213,634 entities, 238,402 officers, 14,110 intermediaries, 93,454 addresses.

License (checked on the ICIJ page): the database is under the Open Database License (ODbL 1.0), its contents under Creative Commons Attribution-ShareAlike 3.0. ICIJ asks to always cite the International Consortium of Investigative Journalists when using the data.
Suggested citation: International Consortium of Investigative Journalists (ICIJ), *Offshore Leaks Database*, https://offshoreleaks.icij.org, data downloaded 2026-11-06.

The data is not stored in this repository. Raw files are downloaded from the ICIJ link above into `data/` (ignored by git). The exact download steps and the processed subset used are described in the "Reproduce" section once the code exists.

## Graph model (to justify in the report)

- Bipartite graph: officers/intermediaries and entities, linked by "officer of" and "intermediary of".
- One-mode projection on entities, weighted by the number of shared officers, intermediaries or addresses.
- Open choices: directed or undirected, simple graph or multigraph, handling of mass-registration addresses (huge artificial cliques), subset (one jurisdiction or one leak).

## Required report items

- Number of nodes and edges, graph type
- Connectivity and components
- Diameter and radius (method, per component or on the largest one)
- Centralities, with interpretation
- Communities (algorithm, parameters, interpretation)
- Data source, reused code (or none), AI tools used and their purpose

## Structure

```
data/         raw and processed data (or link to external storage)
notebooks/    exploration and analysis
src/          graph construction and analysis code
report/       report sources
figures/      figures used in the report and slides
```

## Reproduce

```bash
uv venv --python 3.12 .venv && uv pip install --python .venv/bin/python -r requirements-lock.txt
mkdir -p data/raw && curl -L -o data/full-oldb.zip https://offshoreleaks-data.icij.org/offshoreleaks/csv/full-oldb.LATEST.zip
unzip data/full-oldb.zip -d data/raw
.venv/bin/python -I src/run_stats.py   # filters Panama Papers, builds both graphs, writes data/processed/stats.json
```

Code: `src/load.py` (CSV filter, cached as parquet), `src/graph.py` (bipartite graph, weighted entity projection, statistics), `src/run_stats.py` (entry point).

## Graph construction (current choices)

- Bipartite graph: entities on one side, officers, intermediaries and entity addresses on the other (undirected, simple, uncapped).
- Entity projection: edge weight = number of shared connectors. Hubs are capped to avoid artificial cliques (a connector with d entities adds d(d-1)/2 edges): officers with more than 500 entities, intermediaries and addresses with more than 50 are ignored in the projection only.
- `registered_address` links are mostly officer to address (145,795 of 151,105), so addresses add little to the entity projection.

## Basic statistics (Panama Papers)

| | Bipartite | Entity projection |
|---|---|---|
| Nodes | 468,623 | 213,634 |
| Edges | 511,687 | 1,238,967 |
| Components | 12,218 | 139,643 (129,607 isolated) |
| Largest component | 310,904 (66.3 %) | 26,643 (12.5 %) |
| Max degree | 7,016 | 720 |


## Milestones

1. Download data, check license, pick subset
2. Build graph, basic statistics, connectivity, diameter and radius
3. Centralities and Louvain, interpretation
4. Report and repository README
5. Slides and rehearsal

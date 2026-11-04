# Offshore network analysis (Graph Analytics project 2026)

Course: MSA-DAT07-05 Graph Analytics (Gianluca Quercini). Group of 3 (exception to the usual limit of 2, approved by the course): Achille Krotoff, Jad Yousri, Adrian Ravas.

- **Report deadline:** 10 November 2026, 8:00 AM (PDF, 15 pages max, template on Inside)
- **Oral defense:** 10 November 2026, between 2:00 PM and 5:00 PM (8 min talk + 2 min questions, both students speak)
- **Software:** NetworkX (Python)

## Question

Who structures the offshore network? Compare central intermediaries and jurisdictions (degree, betweenness, PageRank) with the communities found by Louvain, and check whether communities follow jurisdictions or the leak of origin (Panama, Paradise, Pandora Papers).

## Data

ICIJ Offshore Leaks Database (CSV bulk download): https://offshoreleaks.icij.org/pages/database
License and citation: to verify on the ICIJ page and cite in the report.

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

TODO: fill once the code exists (environment, data download, run order).

## Milestones

1. Download data, check license, pick subset
2. Build graph, basic statistics, connectivity, diameter and radius
3. Centralities and Louvain, interpretation
4. Report and repository README
5. Slides and rehearsal

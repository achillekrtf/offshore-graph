---
title: "Who structures the offshore network of the Panama Papers?"
subtitle: "Graph Analytics 2026 (MSA-DAT07-05), project report"
author: "Achille Krotoff, Jad Yousri, Adrian Ravas"
date: "10 November 2026"
---

> DRAFT. Sections marked **[TODO]** wait for a teammate or for a final check. Replace this header with the Inside template before submission.

## 1. Introduction and question

The Panama Papers leak (2016) exposed the client files of the law firm Mossack Fonseca: thousands of offshore companies, the people behind them and the intermediaries that ordered them. The International Consortium of Investigative Journalists (ICIJ) published the structure as a graph.

**Question.** Who structures the offshore network of the Panama Papers? We identify the central intermediaries, officers and jurisdictions (degree, betweenness, PageRank), then check whether the communities found by Louvain follow the jurisdictions of the entities, the countries of the officers, or the intermediaries.

**Scope.** We work on the Panama Papers only. The brief also mentions Paradise and Pandora Papers. The Pandora Papers entities have no relationship in the ICIJ bulk file, so no Pandora graph can be built. A single leak keeps the graph coherent and computable, and comparing communities with the leak of origin is therefore out of scope.

## 2. Data

**Source.** ICIJ Offshore Leaks Database, bulk CSV (`full-oldb.LATEST.zip`, generated 2026-09-09), https://offshoreleaks.icij.org/pages/database, downloaded 2026-11-06. License: the database is under the Open Database License (ODbL 1.0) and its contents under Creative Commons Attribution-ShareAlike 3.0. ICIJ asks users to cite the International Consortium of Investigative Journalists.

**Structure.** The database is a graph stored in CSV files, one per node type plus one for links, joined on a unique `node_id`. The column `sourceID` gives the leak of origin and lets us keep the Panama Papers.

| Node type | Meaning | Count (Panama Papers) |
|---|---|---|
| Entity | Offshore company, trust or foundation | 213,634 |
| Officer | Person or company that owns, directs or fronts an entity (including nominees) | 238,402 |
| Intermediary | Law firm, bank or agent that ordered the structure | 14,110 |
| Address | Postal address | 93,454 |

Three relationship types connect an entity to the rest of the network: `officer_of` (309,363 links), `intermediary_of` (213,634) and `registered_address` (151,105). The other types in the database (`same_name_as`, `similar`...) are deduplication hints from ICIJ and are ignored. Most `registered_address` links go from an officer to an address (145,795 of 151,105), so addresses add little to the entity graph.

## 3. Graph model

**Bipartite graph.** Entities on one side, connectors (officers, intermediaries, entity addresses) on the other. A link says "this connector is attached to this entity". The graph is undirected, simple and unweighted: only the existence of a link matters for our questions, and the direction of the ICIJ links (connector to entity) carries no further information. It has 468,623 nodes and 511,687 edges.

**Entity projection.** Two entities are linked when they share a connector. The weight is the number of shared connectors. A connector attached to $d$ entities adds $d(d-1)/2$ edges, so the intermediary with 7,016 entities alone would add about 24.6 million edges. We cap the hubs in the projection: officers with more than 500 entities and intermediaries or addresses with more than 50 are ignored when linking entities. This gives 213,634 nodes and 1,238,967 weighted edges. [TODO: sensitivity of the cap (50, 100, 500).]

![Bipartite graph and projection on a toy example](../figures/01_toy_example.png){width=85%}

**Choices that matter.**

- Centralities are computed on the bipartite graph, where intermediaries are nodes, and on the projection, where only entities are.
- Communities are computed on the projection.
- The cap removes the largest hubs from the projection. This lengthens distances and isolates entities that only share a hub connector.

## 4. Basic statistics and connectivity

| | Bipartite | Entity projection |
|---|---|---|
| Nodes | 468,623 | 213,634 |
| Edges | 511,687 | 1,238,967 |
| Density | 4.7e-6 | 5.4e-5 |
| Mean degree | 2.18 | 11.6 |
| Max degree | 7,016 | 720 |
| Connected components | 12,218 | 139,643 |
| Largest component | 310,904 (66.3 %) | 26,643 (12.5 %) |
| Isolated nodes | 0 | 129,607 |

![Degree distributions, log-log](../figures/01_degree_distributions.png){width=90%}

Degrees follow a heavy-tailed distribution: most nodes have one or two links and a few hubs have thousands. In the projection, 129,607 entities (61 %) are isolated: their connectors are shared by nobody, or exceed the cap. The bipartite graph has one giant component and 12,217 small ones.

![Component sizes (rank-size)](../figures/01_component_sizes.png){width=90%}

## 5. Diameter and radius

Distances are in hops, per connected component, since both graphs are disconnected. The diameter is the largest eccentricity and the radius the smallest.

- **Projection:** exact, with a breadth-first search from every node (scipy `csgraph`, 109 s for the largest component).
- **Bipartite giant component** (310,904 nodes): all-pairs is too heavy, so we report a lower bound on the diameter (20 double sweeps) and an upper bound on the radius (eccentricity of the midpoint of the longest path found).

| Graph | Component | Nodes | Diameter | Radius |
|---|---|---|---|---|
| Projection | 1st | 26,643 | 30 | 16 |
| Projection | 2nd to 5th | 115 to 132 | 5 to 9 | 3 to 5 |
| Bipartite | Giant | 310,904 | at least 37 | at most 20 |

![Eccentricity in the largest projection component](../figures/02_eccentricity.png){width=70%}

In the largest projection component, eccentricities are centered around 20 and reach 30, with 74 central nodes of eccentricity 16. A path of length 2 in the bipartite graph (entity, connector, entity) equals one hop in the projection, so the two sets of distances are not comparable directly.

## 6. Centralities

**[TODO: Jad to check this section against notebook 03.]** We compute degree centrality, PageRank (damping 0.85) and betweenness on the bipartite graph and on the projection. Betweenness is estimated by sampling sources (50 on the 311,000-node bipartite giant component, 200 on the projection component, seed 0), because exact betweenness needs a shortest-path tree from every node.

![Highest-degree intermediaries and officers](../figures/03_degree_intermediaries_officers.png){width=95%}

**Intermediaries.** Orion House Services (HK) Limited is attached to 7,016 entities, followed by Mossack Fonseca & Co. (Panama, 4,364), Prime Corporate Solutions SARL (4,117), Offshore Business Consultant (Int'l) Limited (4,094) and Mossack Fonseca & Co. (Singapore, 3,888). The top 15 by degree and by PageRank are the same 15 names, and the rank correlation between the two scores over all intermediaries is 0.92. By betweenness, the Singapore and UK offices of Mossack Fonseca come first and Orion House third.

![Intermediary degree against PageRank](../figures/03_intermediary_degree_pagerank.png){width=80%}

**Officers.** Mossfon Subscribers Ltd. (Samoa) is attached to 3,882 entities, against 368 for the next officer. It is a nominee company, and in a bipartite graph every path between two entities goes through a connector, so this single node carries a large share of the shortest paths.

**Projection.** On the projection, rank correlations between degree, PageRank and betweenness are weak (Spearman 0.2 to 0.65), and none of the 20 most central entities of the bipartite graph appears in the top 20 of the projection. The two graphs answer different questions: the bipartite graph ranks the actors that hold the links, the projection ranks entities that sit between many others.

**Jurisdictions.** Jurisdictions are node attributes, not nodes. The British Virgin Islands hold 113,648 entities, Panama 48,360, the Bahamas 15,915 and the Seychelles 15,182. Among the 50 entities with the highest bipartite PageRank, 37 are in the British Virgin Islands.

![Jurisdiction shares](../figures/03_jurisdiction_shares.png){width=75%}

## 7. Communities

**[TODO: Adrian.]** Louvain on the weighted entity projection (parameters: resolution, seed, number of runs), community size distribution and modularity. Comparison of the communities with three references: the jurisdiction of the entities, the countries of the officers and the dominant intermediary of each community, measured by purity or normalized mutual information. Hypothesis to test: communities follow intermediaries, since a firm creates many entities in the same jurisdictions. The 129,607 isolated entities are excluded from this analysis and the report says so.

## 8. Discussion and limits

- One leak only: no comparison across leaks, and the structure reflects one law firm's clients.
- Hub cap: a modeling choice that changes distances and isolates 61 % of entities in the projection. [TODO: sensitivity result.]
- Sampled betweenness: reliable at the top of the ranking only.
- The bulk file reflects ICIJ's own deduplication and a data cut-off in 2015.
- Names refer to companies and persons published by ICIJ. Presence in the leak does not imply wrongdoing.

## 9. Reproducibility, code and AI tools

- **Code:** Python 3.12, pandas, NetworkX 3.3, scipy, python-louvain, matplotlib. Repository: https://github.com/achillekrtf/offshore-graph (`src/` for the code, `notebooks/` for the analysis, README for the steps to reproduce). The raw data is not stored in the repository.
- **Reused code:** none beyond the libraries above. **[TODO: confirm with Jad and Adrian.]**
- **AI tools used and purpose:** Claude Code (Anthropic) helped to write the loading and graph-construction code, the diameter computation and notebooks 01 and 02, and to draft this report; every number was recomputed by a script and checked by the authors. **[TODO: each member lists their own tools, e.g. Cursor and Neo4j assistance for notebook 03 and the Neo4j dashboard, and for notebook 04.]**

## References

- International Consortium of Investigative Journalists (ICIJ), *Offshore Leaks Database*, https://offshoreleaks.icij.org.
- Hagberg, Schult, Swart, *Exploring network structure, dynamics, and function using NetworkX*, SciPy 2008.
- Blondel, Guillaume, Lambiotte, Lefebvre, *Fast unfolding of communities in large networks*, J. Stat. Mech., 2008.
- Brandes, *A faster algorithm for betweenness centrality*, J. Math. Sociol., 2001.

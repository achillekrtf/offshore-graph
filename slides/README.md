# Oral defense slides (10 November 2026, 8 min + 2 min questions)

Deck (private Claude artifact, 11 slides, code excerpts on slides 4 to 9): https://claude.ai/artifact/VARtnNCLESrMXJw6xAzv6b
`slides/source/` holds the slide files (HTML on a 1920x1080 canvas) and `deck.json`. Speaker notes are in the `<aside>` of each file.

| # | Slide | Speaker | Time |
|---|---|---|---|
| 1 | Cover | Achille | 0:10 |
| 2 | Question, data, tools | Achille | 0:20 |
| 3 | The data: four types of nodes, with examples | Achille | 0:55 |
| 4 | Steps 1 and 2: CSV to bipartite graph (code) | Achille | 0:40 |
| 5 | Step 3: projection and hub cap (code) | Achille | 0:50 |
| 6 | Step 4: components, diameter, radius, stats with examples (code) | Achille | 1:00 |
| 7 | Step 5a: degree and PageRank (code) | Jad | 0:55 |
| 8 | Step 5b: betweenness, jurisdictions (code) | Jad | 0:55 |
| 9 | Step 6: Louvain communities (code) | Adrian | 0:55 |
| 10 | What explains the communities | Adrian | 0:50 |
| 11 | Findings and limits | All | 0:25 |

Jad's and Adrian's notes are drafts built from notebooks 03 and 04: adapt them to your own words and rehearse with a timer. Total about 8 minutes.

## Likely questions
- Why a cap on hubs, and what does it change? (without it one intermediary adds about 24 million edges; distances grow and entities become isolated; sensitivity table in the report, section 3)
- Why 61 % isolated entities? (their connectors are unique, or above the cap; 31 % to 72 % across caps)
- Why sampled betweenness, how reliable? (311,000 nodes; reliable at the top of the ranking only)
- Why Panama Papers only? (Pandora has no relationships in the bulk file)
- Exact or bounded diameter? (exact on the projection, bounds on the bipartite giant component)
- How did you use AI tools? (see the report, section 9)

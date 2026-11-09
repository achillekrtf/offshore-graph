# Oral defense slides (10 November 2026, 8 min + 2 min questions)

Deck (private Claude artifact, 8 slides): https://claude.ai/artifact/VARtnNCLESrMXJw6xAzv6b
`slides/source/` holds the slide files (HTML on a 1920x1080 canvas) and `deck.json`. Speaker notes are in the `<aside>` of each file.

| # | Slide | Speaker | Time |
|---|---|---|---|
| 1 | Cover | Achille | 0:15 |
| 2 | Question and scope | Achille | 0:45 |
| 3 | Two graphs from one dataset (bipartite, projection, hub cap) | Achille | 1:30 |
| 4 | Statistics, connectivity, diameter and radius | Achille | 1:15 |
| 5 | Centralities | Jad | 1:45 |
| 6 | Louvain communities | Adrian | 1:00 |
| 7 | What explains the communities | Adrian | 1:00 |
| 8 | Findings and limits | All | 0:45 |

Jad's and Adrian's notes are drafts built from notebooks 03 and 04: adapt them to your own words and rehearse with a timer. Total about 8 minutes.

## Likely questions
- Why a cap on hubs, and what does it change? (without it one intermediary adds about 24 million edges; distances grow and entities become isolated; sensitivity table in the report, section 3)
- Why 61 % isolated entities? (their connectors are unique, or above the cap; 31 % to 72 % across caps)
- Why sampled betweenness, how reliable? (311,000 nodes; reliable at the top of the ranking only)
- Why Panama Papers only? (Pandora has no relationships in the bulk file)
- Exact or bounded diameter? (exact on the projection, bounds on the bipartite giant component)
- How did you use AI tools? (see the report, section 9)

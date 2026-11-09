"""Sensitivity of the projection to the intermediary cap (50, 100, 500)."""
import sys, json, pickle; sys.path.insert(0, ".")
import networkx as nx
from src.load import load_panama, PROC
from src.graph import edges_entity_connector, build_projection
n, r = load_panama(); d = edges_entity_connector(n, r)
rows = []
for cap in (10, 50, 100, 500):
    P = build_projection(n, d, cap={"officer": 500, "intermediary": cap, "address": 50})
    comps = sorted((len(c) for c in nx.connected_components(P)), reverse=True)
    iso = sum(1 for c in comps if c == 1)
    rows.append({"intermediary_cap": cap, "edges": P.number_of_edges(), "isolated": iso,
                 "isolated_share": round(iso / P.number_of_nodes(), 3), "components": len(comps),
                 "largest_component": comps[0], "largest_share": round(comps[0] / P.number_of_nodes(), 3)})
    print(rows[-1], flush=True)
json.dump(rows, open(PROC / "cap_sensitivity.json", "w"), indent=2)

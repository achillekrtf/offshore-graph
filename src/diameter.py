"""Exact diameter and radius per component (BFS from every node, unweighted hops)."""
import sys, json, pickle, time; sys.path.insert(0, ".")
import networkx as nx
from src.load import PROC

B, P = pickle.load(open(PROC / "graphs.pkl", "rb"))
res = {}
for name, G, top in [("projection", P, 5)]:
    comps = sorted(nx.connected_components(G), key=len, reverse=True)[:top]
    rows = []
    for c in comps:
        t = time.time()
        H = G.subgraph(c)
        ecc = nx.eccentricity(H)  # exact, one BFS per node
        rows.append({"size": len(c), "diameter": max(ecc.values()), "radius": min(ecc.values()),
                     "center_size": sum(1 for v in ecc.values() if v == min(ecc.values())),
                     "seconds": round(time.time() - t, 1)})
        print(rows[-1], flush=True)
    res[name] = rows
json.dump(res, open(PROC / "diameter.json", "w"), indent=2)

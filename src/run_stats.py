import sys, json, pickle; sys.path.insert(0, ".")
from src.load import load_panama, PROC
from src.graph import *
n, r = load_panama()
d = edges_entity_connector(n, r)
print(d.groupby("ckind").size())
B = build_bipartite(n, d); print("bipartite built")
P = build_projection(n, d); print("projection built")
out = [stats(B, "bipartite (entities + officers + intermediaries + addresses)"), stats(P, "entity projection (capped)")]
json.dump(out, open(PROC / "stats.json", "w"), indent=2)
pickle.dump((B, P), open(PROC / "graphs.pkl", "wb"))
for s in out: print(json.dumps(s, indent=1))

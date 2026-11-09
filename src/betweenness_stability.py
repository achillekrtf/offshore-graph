"""How stable is the sampled betweenness ranking of intermediaries? 5 seeds at k=50, then k=300."""
import sys, pickle, time; sys.path.insert(0, ".")
import pandas as pd, networkx as nx
from src.load import load_panama, PROC

B, P = pickle.load(open(PROC / "graphs.pkl", "rb"))
nodes, _ = load_panama(); name = nodes.set_index("node_id").name
giant = max(nx.connected_components(B), key=len); H = B.subgraph(giant)
inter = [n for n, d in B.nodes(data=True) if d["kind"] == "intermediary" and n in giant]
runs = {}
for seed in range(5):
    t = time.time(); bc = nx.betweenness_centrality(H, k=50, normalized=True, seed=seed)
    runs[f"k50_seed{seed}"] = pd.Series({n: bc[n] for n in inter}); print("k=50 seed", seed, round(time.time() - t), "s", flush=True)
t = time.time(); bc = nx.betweenness_centrality(H, k=300, normalized=True, seed=0)
runs["k300_seed0"] = pd.Series({n: bc[n] for n in inter}); print("k=300", round(time.time() - t), "s", flush=True)
R = pd.DataFrame(runs); R.insert(0, "name", name.reindex(R.index).values)
R.to_csv(PROC / "betweenness_stability.csv")
ranks = R.drop(columns="name").rank(ascending=False, method="min")
top = ranks["k300_seed0"].sort_values().head(10).index
pd.set_option("display.width", 250)
print(pd.concat([R.loc[top, "name"], ranks.loc[top].astype(int)], axis=1).to_string())
top6 = {c: set(ranks[c].sort_values().head(6).index) for c in ranks}
print({c: len(top6[c] & top6["k300_seed0"]) for c in top6}, "of 6 in common with the k=300 top 6")

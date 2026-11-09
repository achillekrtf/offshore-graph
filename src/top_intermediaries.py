"""Top intermediaries with degree, PageRank and sampled betweenness (same parameters as notebook 03)."""
import sys, pickle; sys.path.insert(0, ".")
import pandas as pd, networkx as nx
from src.load import load_panama, PROC

B, P = pickle.load(open(PROC / "graphs.pkl", "rb"))
nodes, _ = load_panama(); meta = nodes.set_index("node_id")
nB = B.number_of_nodes()
inter = [n for n, d in B.nodes(data=True) if d["kind"] == "intermediary"]
deg = pd.Series({n: B.degree(n) for n in inter})
pr = nx.pagerank(B, alpha=0.85, tol=1e-6)
giant = max(nx.connected_components(B), key=len)
bc = nx.betweenness_centrality(B.subgraph(giant), k=50, normalized=True, seed=0)
df = pd.DataFrame({"name": meta.name.reindex(inter).values, "countries": meta.countries.reindex(inter).values,
                   "degree": deg.values, "pagerank_x_n": [pr[n] * nB for n in inter],
                   "betweenness": [bc.get(n) for n in inter]}, index=inter)
df["rank_degree"] = df.degree.rank(ascending=False, method="min").astype(int)
df["rank_pagerank"] = df.pagerank_x_n.rank(ascending=False, method="min").astype(int)
df["rank_betweenness"] = df.betweenness.rank(ascending=False, method="min")
df.sort_values("degree", ascending=False).to_csv(PROC / "top_intermediaries.csv")
pd.set_option("display.width", 220); pd.set_option("display.max_columns", 20)
print(df.sort_values("degree", ascending=False).head(10).round(4).to_string())
print("\nTop 5 by betweenness:")
print(df.sort_values("betweenness", ascending=False).head(5)[["name", "countries", "degree", "betweenness", "rank_degree"]].round(4).to_string())
print("\nintermediaries with betweenness estimate:", int(df.betweenness.notna().sum()), "of", len(df))

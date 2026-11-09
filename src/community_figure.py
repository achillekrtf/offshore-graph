"""Draw one real Louvain community twice: colored by jurisdiction, then by intermediary."""
import sys, pickle; sys.path.insert(0, ".")
import numpy as np, pandas as pd, networkx as nx
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.load import load_panama, PROC
from src.graph import edges_entity_connector

B, P = pickle.load(open(PROC / "graphs.pkl", "rb"))
nodes, rels = load_panama(); meta = nodes.set_index("node_id")
d = edges_entity_connector(nodes, rels); inter = d[d.ckind == "intermediary"].set_index("ent").conn
giant = max(nx.connected_components(P), key=len)
G = nx.Graph(); G.add_nodes_from(n for n in P.nodes if n in giant)
G.add_weighted_edges_from((u, v, w["weight"]) for u, v, w in P.edges(data=True) if u in giant and v in giant)
comms = nx.community.louvain_communities(G, weight="weight", resolution=1.0, seed=0)
print("communities", len(comms), "modularity", round(nx.community.modularity(G, comms, weight="weight"), 4))

rows = []
for i, c in enumerate(comms):
    if not 25 <= len(c) <= 70: continue
    ic = inter.reindex(list(c)); jc = pd.Series({n: meta.at[n, "jurisdiction_description"] for n in c})
    rows.append((i, len(c), ic.value_counts(normalize=True).iloc[0], jc.value_counts(normalize=True).iloc[0], ic.nunique()))
cand = pd.DataFrame(rows, columns=["i", "size", "inter_share", "jur_share", "n_inter"])
cand["gap"] = cand.inter_share - cand.jur_share
print(cand.sort_values("gap", ascending=False).head(6).round(2).to_string())
pick = cand[(cand.inter_share >= 0.9) & (cand.jur_share <= 0.75)].sort_values("size", ascending=False)
i = int((pick if len(pick) else cand.sort_values("gap", ascending=False)).iloc[0].i)
c = list(comms[i]); H = G.subgraph(c)
ic = inter.reindex(c); jc = pd.Series({n: meta.at[n, "jurisdiction_description"] for n in c})
print("picked community", i, "size", len(c), "intermediaries", ic.nunique(), ic.map(meta.name).value_counts().head(3).to_dict(), jc.value_counts().head(4).to_dict())

pos = nx.spring_layout(H, weight="weight", seed=7, k=0.35, iterations=200)
pal = ["#1F5FBF", "#D9822B", "#2E9D6B", "#C44E52", "#8172B2", "#8C8C8C"]
def draw(ax, labels, title):
    top = labels.value_counts().index[:5].tolist()
    col = {t: pal[k] for k, t in enumerate(top)}
    nx.draw_networkx_edges(H, pos, ax=ax, width=[0.4 + 0.6 * min(H[u][v]["weight"], 3) for u, v in H.edges()], edge_color="#C9C5BB")
    nx.draw_networkx_nodes(H, pos, ax=ax, node_size=70, node_color=[col.get(labels[n], pal[5]) for n in H], linewidths=0)
    for t, cc in col.items(): ax.scatter([], [], c=cc, s=40, label=str(t)[:34])
    ax.scatter([], [], c=pal[5], s=40, label="others"); ax.legend(frameon=False, fontsize=7, loc="lower center", bbox_to_anchor=(0.5, -0.2), ncol=1)
    ax.set_title(title, fontsize=10); ax.axis("off")
fig, ax = plt.subplots(1, 2, figsize=(9, 4.6))
draw(ax[0], jc, "Colored by jurisdiction")
draw(ax[1], ic.map(meta.name), "Colored by intermediary")
plt.suptitle(f"One Louvain community ({len(c)} entities)", fontsize=11); plt.tight_layout()
plt.savefig("figures/05_community_example.png", dpi=150, bbox_inches="tight")

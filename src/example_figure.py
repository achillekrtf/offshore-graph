"""Draw one small real piece of the network twice: bipartite graph and entity projection."""
import sys, pickle; sys.path.insert(0, ".")
import networkx as nx
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from src.load import PROC

B, P = pickle.load(open(PROC / "graphs.pkl", "rb"))
best = None
for comp in nx.connected_components(B):
    if not 9 <= len(comp) <= 14: continue
    kinds = [B.nodes[n]["kind"] for n in comp]
    if kinds.count("officer") < 2 or kinds.count("intermediary") < 1 or kinds.count("entity") < 5: continue
    H = B.subgraph(comp); ents = [n for n in comp if B.nodes[n]["kind"] == "entity"]
    Pj = P.subgraph(ents)
    score = (max((w for *_, w in Pj.edges(data="weight")), default=0) >= 2, Pj.number_of_edges())
    if best is None or score > best[0]: best = (score, comp, Pj)
score, comp, Pj = best
H = B.subgraph(comp); ents = sorted(n for n in comp if B.nodes[n]["kind"] == "entity")
name = {n: f"E{i+1}" for i, n in enumerate(ents)}
col = {"entity": "#1F5FBF", "officer": "#D9822B", "intermediary": "#2E9D6B", "address": "#C44E52"}
lab = {n: name.get(n, "") for n in H}
print("bipartite piece:", H.number_of_nodes(), "nodes,", H.number_of_edges(), "edges;",
      {k: sum(1 for n in H if B.nodes[n]["kind"] == k) for k in col})
print("projection:", Pj.number_of_nodes(), "nodes,", Pj.number_of_edges(), "edges; weights", sorted(w for *_, w in Pj.edges(data="weight")))
fig, ax = plt.subplots(1, 2, figsize=(11, 4.8))
pos = nx.spring_layout(H, seed=4, k=0.9)
nx.draw_networkx_edges(H, pos, ax=ax[0], edge_color="#999")
nx.draw_networkx_nodes(H, pos, ax=ax[0], node_color=[col[B.nodes[n]["kind"]] for n in H], node_size=[520 if B.nodes[n]["kind"] == "entity" else 380 for n in H])
nx.draw_networkx_labels(H, pos, lab, ax=ax[0], font_size=8, font_color="white")
for k, c in col.items():
    if any(B.nodes[n]["kind"] == k for n in H): ax[0].scatter([], [], c=c, s=60, label=k)
ax[0].legend(frameon=False, fontsize=8, loc="lower left"); ax[0].set_title("Bipartite graph: entities and connectors"); ax[0].axis("off")
pj = nx.spring_layout(Pj, seed=2, k=1.2)
nx.draw_networkx_edges(Pj, pj, ax=ax[1], width=[1 + 2 * w for *_, w in Pj.edges(data="weight")], edge_color="#999")
nx.draw_networkx_nodes(Pj, pj, ax=ax[1], node_color=col["entity"], node_size=520)
nx.draw_networkx_labels(Pj, pj, name, ax=ax[1], font_size=8, font_color="white")
nx.draw_networkx_edge_labels(Pj, pj, {(u, v): w for u, v, w in Pj.edges(data="weight")}, ax=ax[1], font_size=8)
ax[1].set_title("Projection on the entities (edge label = shared connectors)"); ax[1].axis("off")
plt.suptitle("The same small piece of the real network, drawn two ways", fontsize=11); plt.tight_layout()
plt.savefig("figures/06_real_bipartite_vs_projection.png", dpi=150, bbox_inches="tight")

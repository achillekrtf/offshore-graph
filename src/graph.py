"""Build the bipartite graph and the weighted entity projection for Panama Papers."""
import numpy as np
import pandas as pd
import networkx as nx
import scipy.sparse as sp
from src.load import load_panama

# Hubs are capped in the projection: a connector linked to d entities adds d(d-1)/2 edges.
CAP = {"officer": 500, "intermediary": 50, "address": 50}


def edges_entity_connector(nodes, rels):
    kind = nodes.set_index("node_id").kind
    ent = set(nodes.node_id[nodes.kind == "entity"])
    o = rels[rels.rel_type == "officer_of"].rename(columns={"node_id_start": "conn", "node_id_end": "ent"})
    i = rels[rels.rel_type == "intermediary_of"].rename(columns={"node_id_start": "conn", "node_id_end": "ent"})
    a = rels[rels.rel_type == "registered_address"].rename(columns={"node_id_end": "conn", "node_id_start": "ent"})
    d = pd.concat([o, i, a])[["conn", "ent"]].drop_duplicates()
    d = d[d.ent.isin(ent)]
    d["ckind"] = d.conn.map(kind)
    return d[d.ckind.notna()]


def build_bipartite(nodes, d):
    meta = nodes.set_index("node_id")
    G = nx.Graph()
    ents = set(d.ent)
    G.add_nodes_from(((n, {"kind": "entity", "jur": meta.at[n, "jurisdiction_description"]}) for n in ents))
    for k, grp in d.groupby("ckind"):
        G.add_nodes_from((c, {"kind": k}) for c in grp.conn.unique())
    G.add_edges_from(zip(d.conn, d.ent))
    # entities with no kept link still belong to the dataset
    for n in nodes.node_id[nodes.kind == "entity"]:
        if n not in G:
            G.add_node(n, kind="entity", jur=meta.at[n, "jurisdiction_description"])
    return G


def build_projection(nodes, d, cap=CAP):
    meta = nodes.set_index("node_id")
    ent_ids = nodes.node_id[nodes.kind == "entity"].tolist()
    eidx = {e: k for k, e in enumerate(ent_ids)}
    W = sp.csr_matrix((len(ent_ids), len(ent_ids)), dtype=np.int32)
    for kind, c in cap.items():
        s = d[d.ckind == kind]
        deg = s.groupby("conn").ent.nunique()
        keep = deg[deg <= c].index
        s = s[s.conn.isin(keep)]
        cidx = {x: k for k, x in enumerate(keep)}
        B = sp.csr_matrix((np.ones(len(s), dtype=np.int32),
                           (s.ent.map(eidx).values, s.conn.map(cidx).values)),
                          shape=(len(ent_ids), len(cidx)))
        W = W + (B @ B.T)
    W = sp.triu(W, k=1).tocoo()
    P = nx.Graph()
    P.add_nodes_from((e, {"jur": meta.at[e, "jurisdiction_description"]}) for e in ent_ids)
    P.add_weighted_edges_from(zip((ent_ids[i] for i in W.row), (ent_ids[j] for j in W.col), W.data.tolist()))
    return P


def stats(G, name):
    comps = sorted((len(c) for c in nx.connected_components(G)), reverse=True)
    deg = np.array([x for _, x in G.degree()])
    return {
        "graph": name, "nodes": G.number_of_nodes(), "edges": G.number_of_edges(),
        "type": "undirected simple" + (", weighted" if nx.is_weighted(G) else ""),
        "density": nx.density(G), "mean_degree": float(deg.mean()), "max_degree": int(deg.max()),
        "isolated": int((deg == 0).sum()), "components": len(comps),
        "largest_component": comps[0], "largest_share": comps[0] / G.number_of_nodes(),
        "top5_components": comps[:5], "singleton_components": int(sum(1 for c in comps if c == 1)),
    }

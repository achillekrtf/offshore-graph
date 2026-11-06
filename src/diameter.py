"""Diameter and radius per component, in hops (unweighted).

Projection: exact (BFS from every node, scipy csgraph, chunked).
Bipartite: the largest component is too big for all-pairs, so we report a lower bound
on the diameter (repeated double sweep) and an upper bound on the radius (eccentricity of the best path midpoint).
"""
import sys, json, pickle, time; sys.path.insert(0, ".")
import numpy as np, networkx as nx, scipy.sparse as sp
from scipy.sparse.csgraph import shortest_path, breadth_first_order
from src.load import PROC


def csr(G, nodes):
    idx = {n: i for i, n in enumerate(nodes)}
    e = [(idx[u], idx[v]) for u, v in G.subgraph(nodes).edges()]
    r, c = zip(*e)
    n = len(nodes)
    A = sp.coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n)).tocsr()
    return (A + A.T).tocsr()


def exact(A, chunk=400):
    n = A.shape[0]; ecc = np.zeros(n)
    for s in range(0, n, chunk):
        D = shortest_path(A, method="D", unweighted=True, indices=np.arange(s, min(s + chunk, n)))
        ecc[s:s + chunk] = D.max(axis=1)
    return ecc


def sweep(A, start):
    """Double sweep: returns (diameter lower bound, eccentricity of the midpoint of the found path).
    The midpoint eccentricity is a valid upper bound on the radius."""
    d = shortest_path(A, method="D", unweighted=True, indices=[start])[0]
    a = int(np.argmax(np.where(np.isinf(d), -1, d)))
    da = shortest_path(A, method="D", unweighted=True, indices=[a])[0]
    b = int(np.argmax(np.where(np.isinf(da), -1, da)))
    db = shortest_path(A, method="D", unweighted=True, indices=[b])[0]
    mid = int(np.argmin(np.where(np.isinf(da) | np.isinf(db), 10**9, np.maximum(da, db))))
    ecc_mid = shortest_path(A, method="D", unweighted=True, indices=[mid])[0].max()
    return int(da.max()), int(ecc_mid)


if __name__ == "__main__":
    B, P = pickle.load(open(PROC / "graphs.pkl", "rb"))
    res = {"projection_exact": [], "bipartite_bounds": None}
    comps = sorted(nx.connected_components(P), key=len, reverse=True)[:5]
    for c in comps:
        t = time.time(); nodes = list(c); A = csr(P, nodes); ecc = exact(A)
        row = {"size": len(nodes), "diameter": int(ecc.max()), "radius": int(ecc.min()),
               "n_center_nodes": int((ecc == ecc.min()).sum()), "seconds": round(time.time() - t, 1)}
        print(row, flush=True); res["projection_exact"].append(row)
    json.dump(res, open(PROC / "diameter.json", "w"), indent=2)

    big = list(max(nx.connected_components(B), key=len)); A = csr(B, big)
    rng = np.random.default_rng(0); lb = 0; best_ecc = 10**9; t = time.time()
    for s in rng.choice(len(big), 20, replace=False):
        dia, em = sweep(A, int(s)); lb = max(lb, dia)
        best_ecc = min(best_ecc, em)
    res["bipartite_bounds"] = {"size": len(big), "diameter_lower_bound": lb,
                               "radius_upper_bound": best_ecc, "sweeps": 20, "seconds": round(time.time() - t, 1)}
    print(res["bipartite_bounds"])
    json.dump(res, open(PROC / "diameter.json", "w"), indent=2)

import sys; sys.path.insert(0, ".")
import pandas as pd
from src.load import load_panama
n, r = load_panama()
kind = n.set_index("node_id").kind
r = r.assign(ekind=r.node_id_end.map(kind), skind=r.node_id_start.map(kind))
print(r.groupby(["rel_type","skind","ekind"]).size())
# connector -> entity edges
ent = n[n.kind=="entity"].node_id
c = r[r.rel_type=="officer_of"].rename(columns={"node_id_start":"conn","node_id_end":"ent"})
i = r[r.rel_type=="intermediary_of"].rename(columns={"node_id_start":"conn","node_id_end":"ent"})
a = r[r.rel_type=="registered_address"].rename(columns={"node_id_end":"conn","node_id_start":"ent"})
for name, d in [("officer", c), ("intermediary", i), ("address", a)]:
    d = d[d.ent.isin(set(ent))]
    deg = d.groupby("conn").ent.nunique()
    pairs = (deg*(deg-1)//2)
    print(name, "connectors", len(deg), "max deg", deg.max(), "p99", deg.quantile(.99))
    for cap in [10, 50, 100, 500, 1000, 10**9]:
        print("  cap", cap, "pairs", int(pairs[deg<=cap].sum()), "connectors kept", int((deg<=cap).sum()))

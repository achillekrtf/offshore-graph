"""Load the Panama Papers subset of the ICIJ Offshore Leaks CSVs into tidy tables.

Usage: from src.load import load_panama; nodes, rels = load_panama()
Raw files live in data/raw/ (not versioned). Output is cached in data/processed/.
"""
from pathlib import Path
import pandas as pd

RAW = Path(__file__).resolve().parents[1] / "data" / "raw"
PROC = Path(__file__).resolve().parents[1] / "data" / "processed"
LEAK = "Panama Papers"
REL_TYPES = ["officer_of", "intermediary_of", "registered_address"]
NODE_FILES = {
    "entity": ("nodes-entities.csv", ["node_id", "name", "jurisdiction_description", "status", "sourceID"]),
    "officer": ("nodes-officers.csv", ["node_id", "name", "countries", "sourceID"]),
    "intermediary": ("nodes-intermediaries.csv", ["node_id", "name", "countries", "sourceID"]),
    "address": ("nodes-addresses.csv", ["node_id", "address", "countries", "sourceID"]),
}


def load_panama(use_cache=True):
    PROC.mkdir(parents=True, exist_ok=True)
    pn, pr = PROC / "nodes.parquet", PROC / "rels.parquet"
    if use_cache and pn.exists() and pr.exists():
        return pd.read_parquet(pn), pd.read_parquet(pr)
    frames = []
    for kind, (fname, cols) in NODE_FILES.items():
        df = pd.read_csv(RAW / fname, usecols=cols, dtype=str, low_memory=False)
        df = df[df.sourceID == LEAK].copy()
        df["kind"] = kind
        if kind == "address":
            df["name"] = df["address"]
        if "jurisdiction_description" not in df:
            df["jurisdiction_description"] = None
        frames.append(df[["node_id", "name", "kind", "jurisdiction_description", "countries"]]
                      if "countries" in df else
                      df.assign(countries=None)[["node_id", "name", "kind", "jurisdiction_description", "countries"]])
    nodes = pd.concat(frames, ignore_index=True)
    rels = pd.read_csv(RAW / "relationships.csv", usecols=["node_id_start", "node_id_end", "rel_type", "sourceID"], dtype=str)
    rels = rels[(rels.sourceID == LEAK) & rels.rel_type.isin(REL_TYPES)]
    ids = set(nodes.node_id)
    rels = rels[rels.node_id_start.isin(ids) & rels.node_id_end.isin(ids)].drop(columns="sourceID")
    nodes.to_parquet(pn)
    rels.to_parquet(pr)
    return nodes, rels

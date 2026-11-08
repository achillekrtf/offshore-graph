"""Load the Panama Papers subset into Neo4j.

Nodes get a shared :Panama label plus Entity, Officer, Intermediary, or Address.
Relationships keep the CSV direction: OFFICER_OF, INTERMEDIARY_OF, REGISTERED_ADDRESS.

Credentials come from NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, and NEO4J_DATABASE.
If the password is unset, the script reads .cursor/mcp.json.

Usage: .venv/bin/python -u src/import_neo4j.py
"""
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, ".")

import pandas as pd
from neo4j import GraphDatabase

from src.load import load_panama

ROOT = Path(__file__).resolve().parents[1]
BATCH = 5_000
LABEL = {
    "entity": "Entity",
    "officer": "Officer",
    "intermediary": "Intermediary",
    "address": "Address",
}
REL = {
    "officer_of": "OFFICER_OF",
    "intermediary_of": "INTERMEDIARY_OF",
    "registered_address": "REGISTERED_ADDRESS",
}


def credentials():
    uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    user = os.environ.get("NEO4J_USERNAME", "neo4j")
    password = os.environ.get("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE", "neo4j")
    if not password:
        cfg = json.loads((ROOT / ".cursor" / "mcp.json").read_text())
        env = cfg["mcpServers"]["neo4j-mcp"]["env"]
        uri = env.get("NEO4J_MCP_URI", uri)
        user = env.get("NEO4J_MCP_USERNAME", user)
        password = env["NEO4J_MCP_PASSWORD"]
        database = env.get("NEO4J_MCP_DATABASE", database)
    return uri, user, password, database


def rows(df):
    out = df.astype(object).where(pd.notna(df), None)
    return out.to_dict("records")


def batches(records):
    for i in range(0, len(records), BATCH):
        yield records[i : i + BATCH], i


def run(session, query, params=None):
    session.run(query, params or {}).consume()


def main():
    nodes, rels = load_panama()
    uri, user, password, database = credentials()
    driver = GraphDatabase.driver(uri, auth=(user, password))
    driver.verify_connectivity()
    print(f"connected to {uri} database={database}", flush=True)

    with driver.session(database=database) as session:
        run(
            session,
            "CREATE CONSTRAINT panama_node_id IF NOT EXISTS "
            "FOR (n:Panama) REQUIRE n.node_id IS UNIQUE",
        )
        for kind, label in LABEL.items():
            part = nodes.loc[nodes.kind == kind, ["node_id", "name", "jurisdiction_description", "countries"]]
            part = part.rename(columns={"jurisdiction_description": "jurisdiction"})
            recs = rows(part)
            query = (
                "UNWIND $rows AS row "
                f"MERGE (n:Panama {{node_id: row.node_id}}) "
                f"SET n:{label}, n.name = row.name, n.jurisdiction = row.jurisdiction, n.countries = row.countries"
            )
            for batch, start in batches(recs):
                run(session, query, {"rows": batch})
                print(f"{label} {start + len(batch)}/{len(recs)}", flush=True)

        for rel_type, rel_label in REL.items():
            part = rels.loc[rels.rel_type == rel_type, ["node_id_start", "node_id_end"]]
            part = part.rename(columns={"node_id_start": "start", "node_id_end": "end"})
            recs = rows(part)
            query = (
                "UNWIND $rows AS row "
                "MATCH (a:Panama {node_id: row.start}), (b:Panama {node_id: row.end}) "
                f"MERGE (a)-[:{rel_label}]->(b)"
            )
            for batch, start in batches(recs):
                run(session, query, {"rows": batch})
                print(f"{rel_label} {start + len(batch)}/{len(recs)}", flush=True)

        counts = session.run(
            "MATCH (n:Panama) "
            "RETURN count(n) AS nodes, "
            "count { MATCH ()-[r]->() } AS rels"
        ).single()
        print(f"done nodes={counts['nodes']} relationships={counts['rels']}", flush=True)
    driver.close()


if __name__ == "__main__":
    main()

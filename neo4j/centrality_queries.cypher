// Live degree centrality. n - 1 = 468622 on the bipartite graph used in the notebook.
// Intermediary degree = number of entities served.

MATCH (i:Intermediary)-[:INTERMEDIARY_OF]->(e:Entity)
RETURN i.name AS name, i.countries AS countries, count(e) AS degree,
       toFloat(count(e)) / 468622 AS degree_centrality
ORDER BY degree DESC
LIMIT 15;

MATCH (o:Officer)-[:OFFICER_OF]->(e:Entity)
RETURN o.name AS name, o.countries AS countries, count(e) AS degree
ORDER BY degree DESC
LIMIT 15;

MATCH (e:Entity)
WITH e,
  COUNT { (e)<-[:OFFICER_OF]-() }
  + COUNT { (e)<-[:INTERMEDIARY_OF]-() }
  + COUNT { (e)-[:REGISTERED_ADDRESS]->(:Address) } AS degree
RETURN e.name AS name, e.jurisdiction AS jurisdiction, degree,
       toFloat(degree) / 468622 AS degree_centrality
ORDER BY degree DESC
LIMIT 15;

MATCH (e:Entity)
WITH e.jurisdiction AS jurisdiction, count(*) AS entities
RETURN jurisdiction, entities
ORDER BY entities DESC
LIMIT 12;

// PageRank and betweenness were computed in notebooks/03_centralities.ipynb
// and stored here, because this server does not have the GDS algorithm library.
MATCH (n:CentralityScore {graph: 'bipartite', measure: 'pagerank', kind: 'intermediary'})
RETURN n.rank AS rank, n.name AS name, n.extra AS countries, n.score AS pagerank
ORDER BY rank;

MATCH (n:CentralityScore {graph: 'bipartite', measure: 'betweenness', kind: 'intermediary'})
RETURN n.rank AS rank, n.name AS name, n.extra AS countries, n.score AS betweenness
ORDER BY rank;

MATCH (n:CentralityScore {graph: 'projection', measure: 'pagerank', kind: 'entity'})
RETURN n.rank AS rank, n.name AS name, n.extra AS jurisdiction, n.score AS pagerank
ORDER BY rank;

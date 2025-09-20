from fastapi import FastAPI
from models import Node, Edge
from db import driver, create_indexes

app = FastAPI(title="Knowledge Graph API", description="知识图谱管理系统后端")

# ---------------- 初始化 ----------------
@app.on_event("startup")
def startup_event():
    create_indexes()

# ---------------- 节点接口 ----------------
@app.get("/api/query/node")
def query_node(label: str, key: str, value: str, limit: int = 50, skip: int = 0):
    with driver.session() as session:
        cypher = f"""
        MATCH (n:{label} {{{key}: $value}})
        RETURN n
        SKIP $skip LIMIT $limit
        """
        result = session.run(cypher, value=value, skip=skip, limit=limit)
        nodes = [dict(record["n"]) for record in result]
    return {"nodes": nodes}

@app.post("/api/add/node")
def add_node(node: Node):
    with driver.session() as session:
        cypher = f"CREATE (n:{node.label} $props) RETURN n"
        result = session.run(cypher, props=node.properties)
        created = [dict(record["n"]) for record in result]
    return {"created": created}

@app.delete("/api/delete/node")
def delete_node(label: str, key: str, value: str):
    with driver.session() as session:
        cypher = f"MATCH (n:{label} {{{key}: $value}}) DETACH DELETE n"
        session.run(cypher, value=value)
    return {"deleted": f"节点 {label}({key}={value}) 已删除"}

@app.patch("/api/update/node")
def update_node(label: str, key: str, value: str, updates: dict):
    with driver.session() as session:
        cypher = f"""
        MATCH (n:{label} {{{key}: $value}})
        SET n += $updates
        RETURN n
        """
        result = session.run(cypher, value=value, updates=updates)
        updated = [dict(record["n"]) for record in result]
    return {"updated": updated}

# ---------------- 关系接口 ----------------
@app.post("/api/add/edge")
def add_edge(edge: Edge):
    with driver.session() as session:
        cypher = f"""
        MATCH (a:{edge.start_label} {{id: $start_id}})
        MATCH (b:{edge.end_label} {{id: $end_id}})
        CREATE (a)-[r:{edge.relation} $props]->(b)
        RETURN r
        """
        result = session.run(cypher, start_id=edge.start_node_id, end_id=edge.end_node_id, props=edge.properties)
        rels = [dict(record["r"]) for record in result]
    return {"created_relation": rels}

@app.delete("/api/delete/edge")
def delete_edge(start_label: str, start_id: str, end_label: str, end_id: str, relation: str):
    with driver.session() as session:
        cypher = f"""
        MATCH (a:{start_label} {{id: $start_id}})-[r:{relation}]->(b:{end_label} {{id: $end_id}})
        DELETE r
        """
        session.run(cypher, start_id=start_id, end_id=end_id)
    return {"deleted": f"关系 {start_id}-[:{relation}]->{end_id} 已删除"}

@app.patch("/api/update/edge")
def update_edge(start_label: str, start_id: str, end_label: str, end_id: str, relation: str, updates: dict):
    with driver.session() as session:
        cypher = f"""
        MATCH (a:{start_label} {{id: $start_id}})-[r:{relation}]->(b:{end_label} {{id: $end_id}})
        SET r += $updates
        RETURN r
        """
        result = session.run(cypher, start_id=start_id, end_id=end_id, updates=updates)
        updated = [dict(record["r"]) for record in result]
    return {"updated": updated}

# ---------------- 高级查询 ----------------
@app.get("/api/search")
def search_entities(q: str, limit: int = 10):
    with driver.session() as session:
        cypher = """
        CALL db.index.fulltext.queryNodes('entitySearchIndex', $q)
        YIELD node, score
        RETURN node.id AS id, node.name AS name, labels(node)[0] AS type, node.abstract AS abstract
        ORDER BY score DESC
        LIMIT $limit
        """
        result = session.run(cypher, q=q, limit=limit)
        return {"results": [dict(r) for r in result]}

# 一度邻居 + 动态过滤
@app.get("/api/entity/{entity_id}/neighbors")
def get_neighbors(entity_id: str, relationType: str = None, nodeLabel: str = None):
    with driver.session() as session:
        cypher = """
        MATCH (n {id: $entity_id})
        OPTIONAL MATCH (n)-[r]->(m)
        WHERE ($relationType IS NULL OR type(r) = $relationType)
          AND ($nodeLabel IS NULL OR any(lbl IN labels(m) WHERE lbl = $nodeLabel))
        RETURN n AS centerNode,
               collect(DISTINCT {relationship: r, node: m}) AS outbound
        """
        result = session.run(cypher, entity_id=entity_id, relationType=relationType, nodeLabel=nodeLabel)
        return [record.data() for record in result]

# 最短路径
@app.get("/api/path")
def shortest_path(start: str, end: str, max_hops: int = 5):
    with driver.session() as session:
        cypher = """
        MATCH (a {id: $start}), (b {id: $end})
        MATCH p = shortestPath((a)-[*..$max_hops]-(b))
        RETURN p
        """
        result = session.run(cypher, start=start, end=end, max_hops=max_hops)
        return {"paths": [record["p"] for record in result]}

# 时间线
@app.get("/api/timeline/{entity_id}")
def timeline(entity_id: str):
    with driver.session() as session:
        cypher = """
        MATCH (p {id: $entity_id})
        OPTIONAL MATCH (p)-[r]->(event)
        WHERE r.date IS NOT NULL OR event.date IS NOT NULL
        WITH r, event, coalesce(r.date, event.date) AS pointInTime
        WHERE pointInTime IS NOT NULL
        RETURN pointInTime, coalesce(r.description, event.name) AS description,
               type(r) AS relationType, properties(r) AS relProperties, event
        ORDER BY pointInTime ASC
        """
        result = session.run(cypher, entity_id=entity_id)
        return {"timeline": [record.data() for record in result]}

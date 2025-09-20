from fastapi import FastAPI
from models import Node, Edge
from db import driver

app = FastAPI(title="Knowledge Graph API", description="基于Neo4j的知识图谱管理系统")

# ---------------- 节点接口 ----------------
@app.get("/query/node")
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

@app.post("/add/node")
def add_node(node: Node):
    with driver.session() as session:
        cypher = f"CREATE (n:{node.label} $props) RETURN n"
        result = session.run(cypher, props=node.properties)
        created = [dict(record["n"]) for record in result]
    return {"created": created}

@app.delete("/delete/node")
def delete_node(label: str, key: str, value: str):
    with driver.session() as session:
        cypher = f"MATCH (n:{label} {{{key}: $value}}) DETACH DELETE n"
        session.run(cypher, value=value)
    return {"deleted": f"节点 {label}({key}={value}) 已删除"}

@app.patch("/update/node")
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
@app.post("/add/edge")
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

@app.delete("/delete/edge")
def delete_edge(start_label: str, start_id: str, end_label: str, end_id: str, relation: str):
    with driver.session() as session:
        cypher = f"""
        MATCH (a:{start_label} {{id: $start_id}})-[r:{relation}]->(b:{end_label} {{id: $end_id}})
        DELETE r
        """
        session.run(cypher, start_id=start_id, end_id=end_id)
    return {"deleted": f"关系 {start_id}-[:{relation}]->{end_id} 已删除"}

@app.patch("/update/edge")
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

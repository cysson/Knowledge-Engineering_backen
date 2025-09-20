from neo4j import GraphDatabase
import csv

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "test123"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def import_nodes(csv_file, label):
    with driver.session() as session, open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            session.run(f"CREATE (n:{label} $props)", props=row)

def import_edges(csv_file, start_label, end_label, relation):
    with driver.session() as session, open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            session.run(
                f"""
                MATCH (a:{start_label} {{id: $start_id}})
                MATCH (b:{end_label} {{id: $end_id}})
                CREATE (a)-[r:{relation} $props]->(b)
                """,
                start_id=row['start_id'], end_id=row['end_id'], props=row
            )

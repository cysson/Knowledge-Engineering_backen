from neo4j import GraphDatabase
import csv

NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "test123"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

# ---------------- 批量导入 CSV ----------------
def import_nodes(csv_file, label):
    """导入节点 CSV，要求包含 id 唯一标识"""
    with driver.session() as session, open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            session.run(f"CREATE (n:{label} $props)", props=row)

def import_edges(csv_file, start_label, end_label, relation):
    """导入关系 CSV，要求包含 start_id 和 end_id"""
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

# ---------------- 索引和约束 ----------------
def create_indexes():
    with driver.session() as session:
        # 唯一约束
        session.run("CREATE CONSTRAINT unique_person_id IF NOT EXISTS FOR (n:Person) REQUIRE n.id IS UNIQUE")
        session.run("CREATE CONSTRAINT unique_org_id IF NOT EXISTS FOR (n:Organisation) REQUIRE n.id IS UNIQUE")
        session.run("CREATE CONSTRAINT unique_place_id IF NOT EXISTS FOR (n:Place) REQUIRE n.id IS UNIQUE")

        # 全文索引
        session.run("""
        CALL db.index.fulltext.createNodeIndex(
            'entitySearchIndex',
            ['Person','Organisation','Place'],
            ['name','name_zh','abstract']
        )
        """)

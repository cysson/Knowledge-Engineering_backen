from pydantic import BaseModel

class Node(BaseModel):
    label: str
    properties: dict

class Edge(BaseModel):
    start_node_id: str
    end_node_id: str
    start_label: str
    end_label: str
    relation: str
    properties: dict = {}

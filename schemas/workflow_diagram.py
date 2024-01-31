from pydantic import BaseModel, Field


class NodeData(BaseModel):
    label: str
    description: str


class Node(BaseModel):
    id: str
    position: dict[str, int]
    data: NodeData
    type: str


class Edge(BaseModel):
    id: str
    source: str
    target: str
    animated: bool


class WorkflowDiagram(BaseModel):
    nodes: list[Node]
    edges: list[Edge]

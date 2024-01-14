from pydantic import BaseModel, UUID4, Field
from schemas.edge_rule import EdgeRule


class Edge(BaseModel):
    id: UUID4
    from_node_id: UUID4
    to_node_id: UUID4
    rules: list[EdgeRule] = Field(default_factory=list)
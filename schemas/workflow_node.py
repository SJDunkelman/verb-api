from pydantic import Field
from schemas.node import NodeModel


class WorkflowNode(NodeModel):
    context_items: dict = Field(default_factory=dict)

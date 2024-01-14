from pydantic import Field
from api.schemas.node import NodeModel


class WorkflowNode(NodeModel):
    context_items: dict = Field(default_factory=dict)

from pydantic import BaseModel, UUID4
from datetime import datetime
from schemas.workflow_node import WorkflowNode
from schemas.edge import Edge
from shared_enum.workflow_stage import WorkflowStage


class WorkflowCreate(BaseModel):
    name: str
    template_id: UUID4
    is_private: bool = False


class WorkflowResponse(BaseModel):
    id: UUID4
    name: str
    created_at: datetime
    is_private: bool
    stage: WorkflowStage
    nodes: list[WorkflowNode]
    edges: list[Edge]

from pydantic import BaseModel, UUID4
from datetime import datetime


class WorkflowNodeOutput(BaseModel):
    id: UUID4
    created_at: datetime
    note: str | None = None
    workflow_node_id: UUID4

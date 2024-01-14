from shared_enum.workflow_stage import WorkflowStage
from pydantic import BaseModel, UUID4
from datetime import datetime


class WorkflowBase(BaseModel):
    name: str


class WorkflowInsert(WorkflowBase):
    created_by_user_id: UUID4
    is_private: bool = False


class WorkflowInDB(WorkflowBase):
    id: UUID4
    created_at: datetime
    is_private: bool
    stage: WorkflowStage

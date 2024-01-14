from pydantic import BaseModel, UUID4, Field


class WorkflowNodeBase(BaseModel):
    workflow_id: UUID4
    name: str
    description: str
    class_name: str
    node_id: UUID4


class WorkflowNodeInsert(WorkflowNodeBase):
    pass


class WorkflowNodeInDB(WorkflowNodeBase):
    id: UUID4
    context_items: dict

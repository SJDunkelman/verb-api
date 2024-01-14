from pydantic import BaseModel, UUID4


class WorkflowTemplateBase(BaseModel):
    name: str
    id: UUID4


class WorkflowTemplateCreate(WorkflowTemplateBase):
    pass


class WorkflowTemplateInDB(WorkflowTemplateBase):
    description: str | None = None

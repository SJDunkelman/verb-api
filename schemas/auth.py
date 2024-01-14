from pydantic import BaseModel, UUID4
from models.workflow import WorkflowInDB


class AuthResponseBase(BaseModel):
    access_token: str
    user_id: UUID4


class UserLogin(BaseModel):
    email: str
    password: str


class UserLoginResponse(AuthResponseBase):
    first_name: str
    onboarded: bool
    last_viewed_workflow_id: UUID4 | None
    workflows: list[WorkflowInDB]

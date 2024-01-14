from pydantic import BaseModel, UUID4
from datetime import datetime


class UserBase(BaseModel):
    id: UUID4
    first_name: str


class UserCreate(UserBase):
    company_id: UUID4 | None = None


class UserInDB(UserBase):
    onboarded: bool
    company_id: UUID4 | None
    last_logged_in_at: datetime | None
    created_at: datetime
    last_viewed_workflow_id: UUID4 | None

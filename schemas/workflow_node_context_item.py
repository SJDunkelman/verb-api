from pydantic import BaseModel
from shared_enum.context_item_type import ContextItemType


class WorkflowNodeContextItem(BaseModel):
    name: str
    class_name: str
    type: ContextItemType

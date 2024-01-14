from pydantic import BaseModel, UUID4
from shared_enum.node_base_type import NodeBaseType


class NodeModel(BaseModel):
    id: UUID4
    name: str
    description: str
    base_type: NodeBaseType
    class_name: str

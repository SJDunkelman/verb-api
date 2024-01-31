from shared_enum.data_object_status import DataObjectStatus
from datetime import datetime
import json
from utils.json_utils import CustomJSONEncoder
from shared_enum.data_object_intent import Intent


def create_data_object_dict(intent: Intent,
                            input_node_id: str,
                            user_id: str,
                            workflow_id: str,
                            pathway_id: str | None = None,
                            target_context_item_class_name: str | None = None,
                            target_node_data_item_class_name: str | None = None,
                            target_node_id: str | None = None):
    metadata = {
        'created_by_user_id': user_id,
        'created_at': datetime.utcnow(),
        'last_modified_by_user_id': user_id,
        'last_modified_at': datetime.utcnow(),
        'current_status': DataObjectStatus.COMPLETED.value,
        'current_workflow_node_id': input_node_id
    }

    data_object_dict = {
        'intent': intent.value,
        'metadata': metadata,
        'workflow_id': workflow_id,
    }

    if intent == Intent.COMPLETE:
        if pathway_id is not None:
            data_object_dict['pathway_id'] = pathway_id
        else:
            raise ValueError("pathway_id must be provided")
    else:
        if target_node_id is not None:
            data_object_dict['target_node_id'] = target_node_id
        else:
            raise ValueError("target_node_id must be provided")

    if intent == Intent.AMEND:
        if target_context_item_class_name is not None:
            data_object_dict['target_context_item_class_name'] = target_context_item_class_name
        else:
            raise ValueError("target_context_item_class_name must be provided")

    elif intent == Intent.RETRIEVE:
        if target_context_item_class_name is not None:
            data_object_dict['target_context_item_class_name'] = target_context_item_class_name
        elif target_node_data_item_class_name is not None:
            data_object_dict['target_node_data_item_class_name'] = target_node_data_item_class_name
        else:
            raise ValueError("Either target_context_item_class_name or target_node_data_item_class_name must be provided")

    return data_object_dict


def send_data_object_to_core(data_object_dict):
    # Serialize the data object dictionary
    serialized_data_object = json.dumps(data_object_dict, cls=CustomJSONEncoder)

    # Send to core service via Redis (Example: Using a list)
    redis_client.lpush('data_objects_queue', serialized_data_object)

from shared_enum.data_object_status import DataObjectStatus
from datetime import datetime
import json
from utils.json_utils import CustomJSONEncoder
from shared_enum.data_object_intent import Intent


def create_data_object_dict(intent: Intent,
                            input_node_id: str,
                            user_id: str,
                            pathway_id: str,
                            workflow_id: str):
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
        'pathway_id': pathway_id,
        'workflow_id': workflow_id,
    }
    return data_object_dict


def send_data_object_to_core(data_object_dict):
    # Serialize the data object dictionary
    serialized_data_object = json.dumps(data_object_dict, cls=CustomJSONEncoder)

    # Send to core service via Redis (Example: Using a list)
    redis_client.lpush('data_objects_queue', serialized_data_object)
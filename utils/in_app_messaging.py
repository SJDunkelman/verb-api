from api.db import supabase_client
from api.models.in_app_message import InAppMessage


def get_previous_in_app_messages(workflow_id: str, limit: int = 20, offset: int = 0) -> list[InAppMessage] | None:
    message_results = supabase_client.table('in_app_message').select('*').eq('workflow_id', workflow_id).limit(limit).offset(offset).order('created_at', desc=True).execute()
    if not len(message_results.data):
        return []
    return [InAppMessage(
        created_at=msg['created_at'],
        role=msg['role'],
        message=msg['message'],
        user_id=msg['user_id'],
    ) for msg in message_results.data]

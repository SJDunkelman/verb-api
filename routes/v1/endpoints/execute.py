from fastapi import APIRouter, Depends
from supabase import Client as SupabaseClient
from shared_enum.data_object_intent import Intent
from utils.security import get_current_user
from dependencies import get_redis, get_db
from utils.data_object_utils import create_data_object_dict
from redis import Redis
from utils.redis_utils import publish_message
from models.in_app_message import InAppMessage, MessageRole

router = APIRouter()


@router.post("/{workflow_id}/complete")
async def complete_workflow(workflow_id: str,
                            redis_client: Redis = Depends(get_redis),
                            user=Depends(get_current_user),
                            db: SupabaseClient = Depends(get_db)):
    # Get pathway of workflow
    pathway_id = 'bde58f5c-8004-40db-9cf3-4d80d18d58f1'  # Master pathway TODO: Get from database
    input_workflow_node_result = db.table('workflow_node').select('id').eq('workflow_id', workflow_id).eq('node_id',
                                                                                                          '9bc7ba9c-2073-4362-b823-376633a2cd75').single().execute()
    input_workflow_node_id = input_workflow_node_result.data['id']
    data_object_dict = create_data_object_dict(intent=Intent.COMPLETE,
                                               input_node_id=input_workflow_node_id,
                                               user_id=user.id,
                                               pathway_id=pathway_id,
                                               workflow_id=workflow_id)
    publish_message(redis_client, "data_objects", data_object_dict)

    # Send user message
    message_result = db.table('in_app_message').insert([{
        'workflow_id': workflow_id,
        'message': "Running the workflow now, please wait...",
        'role': MessageRole.assistant
    }]).execute()
    new_message = InAppMessage(**message_result.data[0])

    # Send it to the workflow chat channel so it is to the user by the open websocket connection
    workflow_chat_channel = f"workflow:{workflow_id}:chat"
    publish_message(redis_client, workflow_chat_channel, new_message.model_dump(mode='json'))


@router.post("/{workflow_node_id}/amend")
async def amend_workflow_node_context_item(workflow_id: str,
                                           redis_client: Redis = Depends(get_redis),
                                           user=Depends(get_current_user),
                                           db: SupabaseClient = Depends(get_db)):
    pass

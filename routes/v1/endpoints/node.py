from fastapi import APIRouter, Depends, HTTPException
from supabase import Client as SupabaseClient
from shared_enum.data_object_intent import Intent
from utils.security import get_current_user
from dependencies import get_redis, get_db
from utils.data_object_utils import create_data_object_dict
from redis import Redis
from utils.redis_utils import publish_message
from models.in_app_message import InAppMessage, MessageRole

router = APIRouter()


@router.post("/{workflow_node_id}/output")
async def get_node_output(workflow_node_id: str,
                          user=Depends(get_current_user),
                          db: SupabaseClient = Depends(get_db)):
    # Check node is an output node
    workflow_node_details_result = db.rpc("get_workflow_node_details", params={'workflow_node_id': workflow_node_id}).execute()
    workflow_node_type = workflow_node_details_result.data[0]['base_type']
    if workflow_node_type != 'OUTPUT':
        raise HTTPException(status_code=400, detail="Node is not an output node")
    output_results = db.table('workflow_node_output').select('*').eq('workflow_node_id', workflow_node_id).execute()



@router.post("/{workflow_node_id}/amend")
async def amend_workflow_node_context_item(workflow_id: str,
                                           redis_client: Redis = Depends(get_redis),
                                           user=Depends(get_current_user),
                                           db: SupabaseClient = Depends(get_db)):
    pass

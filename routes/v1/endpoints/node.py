from fastapi import APIRouter, Depends, HTTPException
from redis import Redis
from starlette.responses import StreamingResponse
from storage3.utils import StorageException
from supabase import Client as SupabaseClient
from io import BytesIO

import schemas
from config import settings
from dependencies import get_redis, get_db
from shared_enum.file_type import FileType
from utils.security import get_current_user

router = APIRouter()


@router.post("/{workflow_node_id}/output", response_model=list[schemas.WorkflowNodeOutput])
async def get_node_output(workflow_node_id: str,
                          # user=Depends(get_current_user),
                          db: SupabaseClient = Depends(get_db)
                          ) -> list[schemas.WorkflowNodeOutput]:
    # Check node is an output node
    workflow_node_details_result = db.rpc("get_workflow_node_details", params={'workflow_node_id': workflow_node_id}).execute()
    workflow_node_type = workflow_node_details_result.data[0]['base_type']
    if workflow_node_type != 'OUTPUT':
        raise HTTPException(status_code=400, detail="Node is not an output node")
    # TODO: Check if correct user
    output_results = db.table('workflow_node_output_file').select('*').eq('workflow_node_id', workflow_node_id).execute()
    if not output_results.data:
        raise HTTPException(status_code=400, detail="No output found")
    return [schemas.WorkflowNodeOutput(**output) for output in output_results.data]


@router.get("/output/{output_file_id}")
async def get_output_file(output_file_id: str,
                        # user=Depends(get_current_user),
                        db: SupabaseClient = Depends(get_db)):
    # Get output file details
    output_file_result = db.table('workflow_node_output_file').select('*').eq('id', output_file_id).execute()
    output_file = output_file_result.data[0]
    file_path = f"{output_file['workflow_node_id']}/{output_file['file_name']}{output_file['extension']}"
    user_file_name = f"{output_file['user_friendly_file_name']}{output_file['extension']}"

    # Determine MIME type using FileType class
    file_extension = output_file['extension']
    try:
        mime_type = FileType(file_extension).mime_type
    except KeyError:
        raise HTTPException(status_code=500, detail="Unsupported file type")

    # To download from storage bucket
    try:
        response = db.storage.from_(settings.WORKFLOW_NODE_OUTPUT_BUCKET).download(file_path)
    except StorageException:
        raise HTTPException(status_code=500, detail="Error downloading file from storage")

    # Stream the file to the user with a user-friendly file name and correct MIME type
    return StreamingResponse(BytesIO(response),
                             media_type=mime_type,
                             headers={
                                 "Content-Disposition": f"attachment; filename=\"{user_file_name}\"",
                                 'Access-Control-Expose-Headers': 'Content-Disposition'
                             })


@router.post("/{workflow_node_id}/amend")
async def amend_workflow_node_context_item(workflow_id: str,
                                           redis_client: Redis = Depends(get_redis),
                                           user=Depends(get_current_user),
                                           db: SupabaseClient = Depends(get_db)):
    pass


@router.get("/{workflow_node_id}/context_items")
async def get_all_workflow_node_context_items(workflow_node_id: str,
                                              db: SupabaseClient = Depends(get_db)):
    # TODO: Add user check
    context_items_result = db.rpc('get_context_items_for_workflow_node', {'input_workflow_node_id': workflow_node_id}).execute()

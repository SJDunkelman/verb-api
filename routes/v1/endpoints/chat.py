import logging
from fastapi import APIRouter, WebSocket, Depends, Cookie, Query
from starlette.websockets import WebSocketDisconnect
from supabase import Client as SupabaseClient
from utils.security import get_user_from_token
from dependencies import get_redis, get_db
import json
import asyncio
from uuid import uuid4
from redis import Redis
from utils.redis_utils import publish_message, subscribe_to_channel
from utils.in_app_messaging import get_previous_in_app_messages
from models.in_app_message import InAppMessage

router = APIRouter()


# @router.post("/test")
# async def test():
#     publish_message("messages", {
#         "workflow_id": "df629f3c-ffc2-43e8-8375-bfda84415aa3",
#         "input_workflow_node_id": "62817448-458c-4c3d-a2e8-5f8ce6606b7f",
#         "user_id": "249bb8f0-2c31-48c0-ac05-37059f638dc2",
#         "message": "Run a campaign",
#     })
#     return {"message": "Hello world"}


@router.websocket("/ws/{workflow_id}")
async def ws_chat_to_workflow(websocket: WebSocket,
                              workflow_id: str,
                              redis_client: Redis = Depends(get_redis),
                              access_token: str = Query(None),
                              db: SupabaseClient = Depends(get_db)):
    user = get_user_from_token(access_token)
    if not user:
        await websocket.close(code=1008)  # Close the connection if the token is invalid
        return

    await websocket.accept()
    logging.info(f"User {user.id} connected to chat for workflow {workflow_id}")

    # Send back previous messages
    previous_messages = get_previous_in_app_messages(workflow_id=workflow_id, limit=20, offset=0)
    previous_messages_dicts = [json.loads(message.model_dump_json()) for message in previous_messages]
    await websocket.send_json(previous_messages_dicts)

    # Update last viewed workflow for user
    db.table('user').update({'last_viewed_workflow_id': workflow_id}).eq('id', user.id).execute()

    # Subscribe to Redis channel for the specific workflow
    workflow_channel_name = f"workflow:{workflow_id}:chat"
    message_queue = await subscribe_to_channel(redis_client, workflow_channel_name)

    try:
        # Create tasks for receiving WebSocket messages and Redis messages
        ws_receive_task = asyncio.create_task(websocket.receive_text())
        redis_receive_task = asyncio.create_task(message_queue.get())

        while True:
            done, pending = await asyncio.wait(
                {ws_receive_task, redis_receive_task},
                return_when=asyncio.FIRST_COMPLETED,
                timeout=1  # Adjust the timeout as necessary
            )

            if ws_receive_task in done:
                try:
                    data = ws_receive_task.result()
                    message_data = json.loads(data)
                    logging.info(message_data)

                    # Generate a unique message ID (if not already provided in message_data)
                    message_id = message_data.get("message_id", str(uuid4()))

                    # Publish message to Redis channel and save to DB
                    publish_message(redis_client, "messages", {
                        "workflow_id": workflow_id,
                        "user_id": user.id,
                        "message": message_data["message"],
                        "message_id": message_id,
                        "input_workflow_node_id": "62817448-458c-4c3d-a2e8-5f8ce6606b7f",  # TODO: Get the input_workflow_node_id based on the specific workflow each time
                    })
                    db.table('in_app_message').insert({
                        "id": message_id,
                        "workflow_id": workflow_id,
                        "user_id": user.id,
                        "message": message_data["message"],
                        "role": "user",
                    }).execute()
                except asyncio.CancelledError:
                    pass

                # Recreate the WebSocket receive task for the next loop
                ws_receive_task = asyncio.create_task(websocket.receive_text())

            if redis_receive_task in done:
                try:
                    redis_message = redis_receive_task.result()
                    if redis_message and redis_message['type'] == 'message':
                        message_data = json.loads(redis_message['data'])
                        logging.info(message_data)
                        # Check if the message is not from the same user
                        try:
                            if message_data["role"] != "user":
                                await websocket.send_text(redis_message['data'])
                        except KeyError:
                            pass
                # try:
                #     await websocket.send_text(json.dumps({"message": "Hello world"}))
                except asyncio.CancelledError:
                    pass

                # Recreate the Redis receive task for the next loop
                redis_receive_task = asyncio.create_task(message_queue.get())

            # Cancel any pending tasks
            for task in pending:
                task.cancel()

    except WebSocketDisconnect:
        await websocket.close()
    finally:
        # Clean up resources (if needed)
        pass


@router.get("/{workflow_id}/history", response_model=list[InAppMessage])
async def get_chat_history(workflow_id: str,
                           offset: int = Query(0, ge=0),
                           limit: int = Query(20, ge=1, le=100)
                           ) -> list[InAppMessage]:
    older_messages = get_previous_in_app_messages(workflow_id=workflow_id, limit=limit, offset=offset)
    return older_messages

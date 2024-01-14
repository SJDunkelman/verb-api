import json
import asyncio


def publish_message(redis_client, channel: str, message_data: dict):
    message_data = json.dumps(message_data).encode('utf-8')
    redis_client.publish(channel, message_data)


async def listen_to_redis(pubsub, message_queue):
    while True:
        message = await asyncio.to_thread(pubsub.get_message, ignore_subscribe_messages=True, timeout=1)
        if message:
            message_queue.put_nowait(message)
        await asyncio.sleep(0.1)


async def subscribe_to_channel(redis_client, channel):
    pubsub = redis_client.pubsub()
    pubsub.subscribe(channel)
    message_queue = asyncio.Queue()

    asyncio.create_task(listen_to_redis(pubsub, message_queue))
    return message_queue


# if __name__ == "__main__":
#     # Example usage
#     publish_message('messages', "Run a campaign")

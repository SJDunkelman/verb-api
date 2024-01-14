from supabase import create_client, Client
from config import settings
import redis


def create_redis_connection_pool():
    return redis.ConnectionPool.from_url(
        url=settings.REDIS_URL,
        decode_responses=True
    )


redis_connection_pool = create_redis_connection_pool()
supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_ANON_KEY)

from db import supabase_client, redis_connection_pool
import redis


def get_db():
    return supabase_client


def get_redis():
    return redis.Redis(connection_pool=redis_connection_pool)


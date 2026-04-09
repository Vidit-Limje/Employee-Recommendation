import redis

redis_client = redis.Redis(
    host="redis",   # change if using docker/cloud
    port=6379,
    db=0,
    decode_responses=True
)
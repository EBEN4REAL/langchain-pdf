import os
import redis

redis_uri = os.getenv("REDIS_URI", "redis://localhost:6379/0")

# Parse the URI properly
client = redis.from_url(
    redis_uri,
    decode_responses=True,
)
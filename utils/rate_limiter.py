import time
from fastapi import HTTPException, Request, status
from utils.redis_client import redis_client


# Config (you can tune these)
RATE_LIMITS = {
    "GET": (100, 60),     # 100 requests per 60 sec
    "POST": (20, 60),     # 20 requests per 60 sec
    "PATCH": (30, 60),
    "DELETE": (10, 60),
}


def get_user_identifier(request: Request):
    # 👇 If using JWT, extract user id from request.state
    # assuming you set it in auth middleware
    user = getattr(request.state, "user", None)

    if user:
        return f"user:{user.user_id}"

    # fallback (IP based)
    return f"ip:{request.client.host}"


def rate_limiter(request: Request):
    method = request.method.upper()

    if method not in RATE_LIMITS:
        return

    limit, window = RATE_LIMITS[method]

    identifier = get_user_identifier(request)

    key = f"rate_limit:{identifier}:{method}"

    current = redis_client.get(key)

    if current and int(current) >= limit:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded for {method}. Try again later."
        )

    pipe = redis_client.pipeline()

    pipe.incr(key, 1)

    # set expiry only if new key
    if not current:
        pipe.expire(key, window)

    pipe.execute()
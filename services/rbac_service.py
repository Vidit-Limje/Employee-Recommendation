# services/rbac_service.py

import json
import redis
import os

redis_client = redis.from_url(os.getenv("REDIS_URL"))

def get_permissions_by_role(role_name, db):
    key = f"role:{role_name}:permissions"

    cached = redis_client.get(key)
    if cached:
        print("✅ CACHE HIT (RBAC)")
        return json.loads(cached)

    print("❌ CACHE MISS → DB HIT (RBAC)")

    # Your DB query (adapt this)
    result = db.execute("""
        SELECT p.name
        FROM role_permission rp
        JOIN permission p ON rp.permission_id = p.permission_id
        WHERE rp.role_name = :role
    """, {"role": role_name})

    permissions = [row[0] for row in result]

    redis_client.set(key, json.dumps(permissions), ex=600)

    return permissions
# utils/permissions.py

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Set, List
import json
import logging

from database.database import get_db
from utils.dependencies import get_current_user
from utils.redis_client import redis_client


# -----------------------------------------------------------
# LOGGER (helps you debug cache behavior)
# -----------------------------------------------------------
logger = logging.getLogger(__name__)


# -----------------------------------------------------------
# GET PERMISSIONS FOR ROLE (WITH REDIS CACHE)
# -----------------------------------------------------------
def get_permissions_for_role(role: str, db: Session) -> Set[str]:
    cache_key = f"role:{role}:permissions"

    # 🔍 1. Try Redis first
    try:
        cached = redis_client.get(cache_key)
        if cached:
            logger.info(f"✅ CACHE HIT (RBAC) → {role}")
            return set(json.loads(cached))
    except Exception as e:
        logger.warning(f"⚠️ Redis GET failed: {e}")

    # 🧠 2. Fetch from DB (ONLY IF CACHE MISS)
    logger.info(f"❌ CACHE MISS → DB HIT (RBAC) → {role}")

    result = db.execute(
        text("""
            SELECT p.name
            FROM role_permission rp
            JOIN permission p ON rp.permission_id = p.permission_id
            WHERE rp.role_name = :role
        """),
        {"role": role}
    ).fetchall()

    permissions: List[str] = [row[0] for row in result]

    # 💾 3. Store in Redis (TTL = 10 minutes)
    try:
        redis_client.setex(
            cache_key,
            600,  # 10 minutes
            json.dumps(permissions)
        )
    except Exception as e:
        logger.warning(f"⚠️ Redis SET failed: {e}")

    return set(permissions)


# -----------------------------------------------------------
# REQUIRE PERMISSION (FASTAPI DEPENDENCY)
# -----------------------------------------------------------
def require_permission(permission_name: str):

    def checker(
        user=Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        role = user.get("role")

        if not role:
            raise HTTPException(
                status_code=403,
                detail="Role missing"
            )

        # ⚡ Fetch permissions (cached)
        permissions = get_permissions_for_role(role, db)

        # 🔐 Check permission
        if permission_name not in permissions:
            raise HTTPException(
                status_code=403,
                detail="Permission denied"
            )

        return user

    return checker


# -----------------------------------------------------------
# CACHE INVALIDATION (VERY IMPORTANT)
# -----------------------------------------------------------
def invalidate_role_permissions(role: str | None = None):
    """
    Clear cache when role/permissions are updated
    """

    try:
        if role:
            # 🎯 Targeted invalidation
            key = f"role:{role}:permissions"
            redis_client.delete(key)
            logger.info(f"🗑️ Cache invalidated for role: {role}")
        else:
            # 🔥 Clear all roles
            keys = list(redis_client.scan_iter("role:*:permissions"))
            if keys:
                redis_client.delete(*keys)
            logger.info("🗑️ Cache invalidated for ALL roles")

    except Exception as e:
        logger.warning(f"⚠️ Redis invalidation failed: {e}")
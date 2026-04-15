# =====================================================
# SKILL ROUTES (RBAC + REDIS + RATE LIMITING)
# =====================================================

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import json

from database.database import get_db
from models.skill import Skill
from schemas.skill_schema import SkillCreate, SkillResponse

# 🔐 RBAC
from utils.permissions import require_permission

# 🔥 REDIS
from utils.redis_client import redis_client

# 🔥 RATE LIMITER
from utils.rate_limiter import rate_limiter


# -----------------------------------------------------
# ROUTER CONFIG (RATE LIMIT APPLIED GLOBALLY)
# -----------------------------------------------------

router = APIRouter(
    prefix="/skills",
    tags=["Skills"],
    dependencies=[Depends(rate_limiter)]   # 🔥 APPLY TO ALL ROUTES
)


# -----------------------------------------------------------
# CREATE SKILL (ADMIN ONLY)
# -----------------------------------------------------------
@router.post("/", response_model=SkillResponse, status_code=201)
def create_skill(
    request: Request,
    skill: SkillCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("skill.create"))
):
    # 🔍 Check duplicate
    existing = db.query(Skill).filter_by(skill_name=skill.skill_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Skill already exists")

    new_skill = Skill(**skill.model_dump())

    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)

    # 🔥 CACHE INVALIDATION
    redis_client.delete("skills:all")

    for key in redis_client.scan_iter("project:*:recommendations"):
        redis_client.delete(key)

    return new_skill


# -----------------------------------------------------------
# GET ALL SKILLS (CACHED)
# -----------------------------------------------------------
@router.get("/", response_model=list[SkillResponse])
def get_skills(
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(require_permission("skill.read"))
):
    cache_key = "skills:all"

    # 🔍 Try Redis
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 🧠 DB fetch
    skills = db.query(Skill).all()

    data = [
        SkillResponse.model_validate(s).model_dump()
        for s in skills
    ]

    # 💾 Store in Redis
    redis_client.setex(cache_key, 300, json.dumps(data))

    return data


# -----------------------------------------------------------
# DELETE SKILL (ADMIN ONLY)
# -----------------------------------------------------------
@router.delete("/{skill_id}")
def delete_skill(
    request: Request,
    skill_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("skill.delete"))
):
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    db.delete(skill)
    db.commit()

    # 🔥 CACHE INVALIDATION
    redis_client.delete("skills:all")

    for key in redis_client.scan_iter("project:*:recommendations"):
        redis_client.delete(key)

    return {"message": "Skill deleted"}
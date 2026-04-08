from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.skill import Skill
from schemas.skill_schema import SkillCreate, SkillResponse

# 🔐 RBAC
from utils.permissions import require_permission


router = APIRouter(prefix="/skills", tags=["Skills"])


# -----------------------------------------------------------
# CREATE SKILL (ADMIN ONLY)
# -----------------------------------------------------------
@router.post("/", response_model=SkillResponse, status_code=201)
def create_skill(
    skill: SkillCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("skill.create"))   # 🔐
):
    # Check duplicate
    existing = db.query(Skill).filter_by(skill_name=skill.skill_name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Skill already exists")

    new_skill = Skill(**skill.model_dump())

    db.add(new_skill)
    db.commit()
    db.refresh(new_skill)

    return new_skill


# -----------------------------------------------------------
# GET ALL SKILLS (ALL USERS)
# -----------------------------------------------------------
@router.get("/", response_model=list[SkillResponse])
def get_skills(
    db: Session = Depends(get_db),
    user=Depends(require_permission("skill.read"))   # 🔐
):
    return db.query(Skill).all()


# -----------------------------------------------------------
# DELETE SKILL (ADMIN ONLY)
# -----------------------------------------------------------
@router.delete("/{skill_id}")
def delete_skill(
    skill_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("skill.delete"))   # 🔐
):
    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    db.delete(skill)
    db.commit()

    return {"message": "Skill deleted"}
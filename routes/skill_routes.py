from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.skill import Skill
from schemas.skill_schema import SkillCreate, SkillResponse

router = APIRouter(prefix="/skills", tags=["Skills"])


# -----------------------------------------------------------
# CREATE SKILL
# -----------------------------------------------------------
@router.post("/", response_model=SkillResponse, status_code=201)
def create_skill(skill: SkillCreate, db: Session = Depends(get_db)):

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
# GET ALL SKILLS
# -----------------------------------------------------------
@router.get("/", response_model=list[SkillResponse])
def get_skills(db: Session = Depends(get_db)):
    return db.query(Skill).all()


# -----------------------------------------------------------
# DELETE SKILL (optional)
# -----------------------------------------------------------
@router.delete("/{skill_id}")
def delete_skill(skill_id: int, db: Session = Depends(get_db)):

    skill = db.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    db.delete(skill)
    db.commit()

    return {"message": "Skill deleted"}
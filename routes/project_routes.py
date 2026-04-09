# -----------------------------------------------------------
# IMPORTS
# -----------------------------------------------------------

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from database.database import get_db
from models.project import Project
from models.project_skill import ProjectSkill
from models.skill import Skill

from schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
    ProjectResponse
)

from schemas.project_skill_schema import (
    ProjectSkillCreate,
    ProjectSkillResponse
)

from services.recommendation_service import recommend_employees_service

# 🔐 RBAC
from utils.permissions import require_permission

# 🔥 REDIS
from utils.redis_client import redis_client


# -----------------------------------------------------------
# ROUTER CONFIG
# -----------------------------------------------------------

router = APIRouter(prefix="/projects", tags=["Projects"])


# -----------------------------------------------------------
# CREATE PROJECT (ADMIN ONLY)
# -----------------------------------------------------------

@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("project.create"))
):
    new_project = Project(**project.model_dump())

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    redis_client.delete("projects:all")

    return new_project


# -----------------------------------------------------------
# GET ALL PROJECTS (CACHED)
# -----------------------------------------------------------

@router.get("/", response_model=list[ProjectResponse])
def get_projects(
    db: Session = Depends(get_db),
    user=Depends(require_permission("project.read"))
):
    cache_key = "projects:all"

    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    projects = db.query(Project).all()

    # ✅ FIX: Use Pydantic
    data = [
        ProjectResponse.model_validate(p).model_dump()
        for p in projects
    ]

    redis_client.setex(cache_key, 300, json.dumps(data))

    return data


# -----------------------------------------------------------
# GET PROJECT BY ID
# -----------------------------------------------------------

@router.get("/{pid}", response_model=ProjectResponse)
def get_project(
    pid: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("project.read"))
):
    project = db.get(Project, pid)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


# -----------------------------------------------------------
# UPDATE PROJECT
# -----------------------------------------------------------

@router.put("/{pid}", response_model=ProjectResponse)
def update_project(
    pid: int,
    project: ProjectUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("project.update"))
):
    proj = db.get(Project, pid)

    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in project.model_dump().items():
        setattr(proj, key, value)

    db.commit()
    db.refresh(proj)

    redis_client.delete("projects:all")
    redis_client.delete(f"project:{pid}:recommendations")

    return proj


# -----------------------------------------------------------
# DELETE PROJECT
# -----------------------------------------------------------

@router.delete("/{pid}")
def delete_project(
    pid: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("project.delete"))
):
    proj = db.get(Project, pid)

    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(proj)
    db.commit()

    redis_client.delete("projects:all")
    redis_client.delete(f"project:{pid}:recommendations")

    return {"message": f"Project {pid} deleted successfully"}


# -----------------------------------------------------------
# RECOMMEND EMPLOYEES (CACHED)
# -----------------------------------------------------------

@router.get("/{pid}/recommendations")
def recommend_employees(
    pid: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("recommendation.read"))
):
    cache_key = f"project:{pid}:recommendations"

    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    result = recommend_employees_service(pid, db)

    redis_client.setex(cache_key, 300, json.dumps(result))

    return result


# -----------------------------------------------------------
# ADD SKILL TO PROJECT
# -----------------------------------------------------------

@router.post("/{pid}/skills", response_model=ProjectSkillResponse)
def add_project_skill(
    pid: int,
    data: ProjectSkillCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("project_skill.manage"))
):
    project = db.get(Project, pid)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    skill = db.get(Skill, data.skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing = db.query(ProjectSkill).filter(
        ProjectSkill.pid == pid,
        ProjectSkill.skill_id == data.skill_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Skill already added")

    project_skill = ProjectSkill(
        pid=pid,
        skill_id=data.skill_id,
        required_level=data.required_level
    )

    db.add(project_skill)
    db.commit()
    db.refresh(project_skill)

    redis_client.delete(f"project:{pid}:recommendations")

    return project_skill


# -----------------------------------------------------------
# GET PROJECT SKILLS
# -----------------------------------------------------------

@router.get("/{pid}/skills", response_model=list[ProjectSkillResponse])
def get_project_skills(
    pid: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("project.read"))
):
    project = db.get(Project, pid)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return db.query(ProjectSkill).filter(ProjectSkill.pid == pid).all()


# -----------------------------------------------------------
# UPDATE PROJECT SKILL
# -----------------------------------------------------------

@router.patch("/{pid}/skills/{skill_id}", response_model=ProjectSkillResponse)
def update_project_skill(
    pid: int,
    skill_id: int,
    data: ProjectSkillCreate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("project_skill.manage"))
):
    project_skill = db.query(ProjectSkill).filter(
        ProjectSkill.pid == pid,
        ProjectSkill.skill_id == skill_id
    ).first()

    if not project_skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    project_skill.required_level = data.required_level

    db.commit()
    db.refresh(project_skill)

    redis_client.delete(f"project:{pid}:recommendations")

    return project_skill


# -----------------------------------------------------------
# DELETE PROJECT SKILL
# -----------------------------------------------------------

@router.delete("/{pid}/skills/{skill_id}")
def delete_project_skill(
    pid: int,
    skill_id: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("project_skill.manage"))
):
    project_skill = db.query(ProjectSkill).filter(
        ProjectSkill.pid == pid,
        ProjectSkill.skill_id == skill_id
    ).first()

    if not project_skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    db.delete(project_skill)
    db.commit()

    redis_client.delete(f"project:{pid}:recommendations")

    return {"message": "Skill removed"}
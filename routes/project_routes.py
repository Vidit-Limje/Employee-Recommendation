from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.project import Project

from schemas.project_schema import (
    ProjectCreate,
    ProjectUpdate,
    ProjectPartialUpdate,
    ProjectResponse
)

from services.recommendation_service import recommend_employees_service

router = APIRouter(prefix="/projects", tags=["Projects"])


# CREATE PROJECT
@router.post("/", status_code=201, response_model=ProjectResponse)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):

    new_project = Project(**project.model_dump())

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


# GET ALL PROJECTS
@router.get("/", response_model=list[ProjectResponse])
def get_projects(db: Session = Depends(get_db)):

    projects = db.query(Project).all()

    return projects


# GET PROJECT BY ID
@router.get("/{pid}", response_model=ProjectResponse)
def get_project(pid: int, db: Session = Depends(get_db)):

    project = db.get(Project, pid)

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


# UPDATE PROJECT
@router.put("/{pid}", response_model=ProjectResponse)
def update_project(pid: int, project: ProjectUpdate, db: Session = Depends(get_db)):

    proj = db.get(Project, pid)

    if proj is None:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in project.model_dump().items():
        setattr(proj, key, value)

    db.commit()
    db.refresh(proj)

    return proj


# DELETE PROJECT
@router.delete("/{pid}")
def delete_project(pid: int, db: Session = Depends(get_db)):

    proj = db.get(Project, pid)

    if proj is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(proj)
    db.commit()

    return {"message": f"Project {pid} deleted successfully"}


# EMPLOYEE RECOMMENDATION
@router.get("/{pid}/recommendations")
def recommend_employees(pid: int, db: Session = Depends(get_db)):

    return recommend_employees_service(pid, db)
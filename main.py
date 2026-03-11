from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_, text 
from database import SessionLocal
from models import Employee, Project
from schemas import (
    EmployeeCreate, EmployeeUpdate, EmployeePartialUpdate,
    ProjectCreate, ProjectUpdate, ProjectPartialUpdate
)

app = FastAPI()


# -----------------------------
# Database Dependency
# -----------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =====================================================
# EMPLOYEE CRUD
# =====================================================

@app.post("/employees")
def add_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):

    new_employee = Employee(**employee.dict())

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return {
        "message": "Employee added successfully",
        "employee": new_employee
    }


@app.get("/employees")
def get_employees(db: Session = Depends(get_db)):

    employees = db.query(Employee).all()

    return {
        "total": len(employees),
        "employees": employees
    }

@app.get("/employees/search")
def search_employee(query: str, db: Session = Depends(get_db)):

    employees = db.query(Employee).filter(
        or_(
            Employee.firstname.ilike(f"%{query}%"),
            Employee.lastname.ilike(f"%{query}%")
        )
    ).all()

    return {
        "total": len(employees),
        "employees": employees
    }


@app.get("/employees/{eid}")
def get_employee(eid: int, db: Session = Depends(get_db)):

    emp = db.query(Employee).filter(Employee.eid == eid).first()

    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return emp


@app.put("/employees/{eid}")
def update_employee(eid: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):

    emp = db.query(Employee).filter(Employee.eid == eid).first()

    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    for key, value in employee.dict().items():
        setattr(emp, key, value)

    db.commit()
    db.refresh(emp)

    return {
        "message": "Employee updated successfully",
        "employee": emp
    }


@app.patch("/employees/{eid}")
def update_employee_partial(eid: int, employee: EmployeePartialUpdate, db: Session = Depends(get_db)):

    emp = db.query(Employee).filter(Employee.eid == eid).first()

    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = employee.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(emp, key, value)

    db.commit()
    db.refresh(emp)

    return {
        "message": "Employee updated successfully",
        "employee": emp
    }


@app.delete("/employees/{eid}")
def delete_employee(eid: int, db: Session = Depends(get_db)):

    emp = db.query(Employee).filter(Employee.eid == eid).first()

    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(emp)
    db.commit()

    return {
        "message": f"Employee with id {eid} deleted successfully"
    }


# =====================================================
# PROJECT CRUD
# =====================================================

@app.post("/projects")
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):

    new_project = Project(**project.dict())

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return new_project


@app.get("/projects")
def get_projects(db: Session = Depends(get_db)):

    projects = db.query(Project).all()

    return {
        "total": len(projects),
        "projects": projects
    }


@app.get("/projects/{pid}")
def get_project(pid: int, db: Session = Depends(get_db)):

    project = db.query(Project).filter(Project.pid == pid).first()

    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    return project


@app.put("/projects/{pid}")
def update_project(pid: int, project: ProjectUpdate, db: Session = Depends(get_db)):

    proj = db.query(Project).filter(Project.pid == pid).first()

    if proj is None:
        raise HTTPException(status_code=404, detail="Project not found")

    for key, value in project.dict().items():
        setattr(proj, key, value)

    db.commit()
    db.refresh(proj)

    return proj


@app.patch("/projects/{pid}")
def update_project_partial(pid: int, project: ProjectPartialUpdate, db: Session = Depends(get_db)):

    proj = db.query(Project).filter(Project.pid == pid).first()

    if proj is None:
        raise HTTPException(status_code=404, detail="Project not found")

    update_data = project.dict(exclude_unset=True)

    for key, value in update_data.items():
        setattr(proj, key, value)

    db.commit()
    db.refresh(proj)

    return proj


@app.delete("/projects/{pid}")
def delete_project(pid: int, db: Session = Depends(get_db)):

    proj = db.query(Project).filter(Project.pid == pid).first()

    if proj is None:
        raise HTTPException(status_code=404, detail="Project not found")

    db.delete(proj)
    db.commit()

    return {"message": f"Project {pid} deleted successfully"}


@app.get("/projects/{pid}/recommendations")
def recommend_employees(pid: int, db: Session = Depends(get_db)):

    # check if project exists
    project = db.query(Project).filter(Project.pid == pid).first()
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")

    query = text("""
        WITH skill_count AS (
            SELECT COUNT(*) AS total_skills
            FROM project_skill
            WHERE pid = :pid
        ),

        skill_scores AS (
            SELECT
                e.eid,
                ps.skill_id,

                (60.0 / sc.total_skills) *
                CASE
                    WHEN es.proficiency_level >= ps.required_level THEN 1
                    WHEN es.proficiency_level >= ps.required_level * 0.66 THEN 0.75
                    WHEN es.proficiency_level >= ps.required_level * 0.33 THEN 0.50
                    ELSE 0.25
                END AS skill_score

            FROM employee e
            JOIN employee_skill es
                ON e.eid = es.eid
            JOIN project_skill ps
                ON es.skill_id = ps.skill_id
            CROSS JOIN skill_count sc
            WHERE ps.pid = :pid
        ),

        employee_skill_total AS (
            SELECT
                eid,
                SUM(skill_score) AS total_skill_score
            FROM skill_scores
            GROUP BY eid
        )

        SELECT
            e.eid,
            e.firstname,
            e.lastname,

            COALESCE(est.total_skill_score,0) AS skill_score,

            CASE
                WHEN p.required_experience = 0 THEN 25
                WHEN e.experience >= p.required_experience THEN 25
                ELSE (e.experience::float / p.required_experience) * 25
            END AS experience_score,

            CASE
                WHEN e.domain = p.domain THEN 10
                ELSE 0
            END AS domain_score,

            CASE
                WHEN e.availability = true THEN 5
                ELSE 0
            END AS availability_score,

            (
                COALESCE(est.total_skill_score,0)
                +
                CASE
                    WHEN p.required_experience = 0 THEN 25
                    WHEN e.experience >= p.required_experience THEN 25
                    ELSE (e.experience::float / p.required_experience) * 25
                END
                +
                CASE
                    WHEN e.domain = p.domain THEN 10
                    ELSE 0
                END
                +
                CASE
                    WHEN e.availability = true THEN 5
                    ELSE 0
                END
            ) AS final_score

        FROM employee e
        LEFT JOIN employee_skill_total est
            ON e.eid = est.eid
        JOIN project p
            ON p.pid = :pid

        ORDER BY final_score DESC
        LIMIT 10
    """)

    result = db.execute(query, {"pid": pid})

    employees = [dict(row._mapping) for row in result]

    return {
        "project_id": pid,
        "recommendations": employees
    }

# =====================================================
# EMPLOYEE ROUTES (JWT + RBAC PROTECTED)
# =====================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.employee import Employee

from utils.dependencies import get_current_user
from utils.permissions import require_permission

from schemas.employee_schema import (
    EmployeeResponse,
    EmployeePartialUpdate
)

router = APIRouter(prefix="/employees", tags=["Employees"])


# -----------------------------------------------------
# GET ALL EMPLOYEES (ADMIN / PERMISSION BASED)
# -----------------------------------------------------

@router.get("/", response_model=list[EmployeeResponse])
def get_all_employees(
    db: Session = Depends(get_db),
    user=Depends(require_permission("employee.read"))
):
    return db.query(Employee).all()


# -----------------------------------------------------
# GET CURRENT LOGGED-IN EMPLOYEE
# -----------------------------------------------------

@router.get("/me", response_model=EmployeeResponse)
def get_my_profile(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if "eid" not in user:
        raise HTTPException(status_code=400, detail="EID missing in token")

    employee = db.query(Employee).filter(
        Employee.eid == user["eid"]
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


# -----------------------------------------------------
# UPDATE CURRENT USER PROFILE (MOST IMPORTANT)
# -----------------------------------------------------

@router.patch("/me", response_model=EmployeeResponse)
def update_my_profile(
    updated_data: EmployeePartialUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("employee.update"))
):
    employee = db.query(Employee).filter(
        Employee.eid == user["eid"]
    ).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = updated_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

    return employee


# -----------------------------------------------------
# GET EMPLOYEE BY ID (ADMIN / PERMISSION BASED)
# -----------------------------------------------------

@router.get("/id/{eid}", response_model=EmployeeResponse)
def get_employee(
    eid: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("employee.read"))
):
    employee = db.query(Employee).filter(Employee.eid == eid).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


# -----------------------------------------------------
# UPDATE EMPLOYEE BY ID (ADMIN OR OWNER)
# -----------------------------------------------------

@router.patch("/id/{eid}", response_model=EmployeeResponse)
def update_employee(
    eid: int,
    updated_data: EmployeePartialUpdate,
    db: Session = Depends(get_db),
    user=Depends(require_permission("employee.update"))
):
    employee = db.query(Employee).filter(Employee.eid == eid).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 🔐 Ownership + Admin override
    if user["role"] != "admin" and user.get("eid") != eid:
        raise HTTPException(status_code=403, detail="Not authorized")

    update_data = updated_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

    return employee


# -----------------------------------------------------
# DELETE EMPLOYEE (ADMIN ONLY VIA PERMISSION)
# -----------------------------------------------------

@router.delete("/id/{eid}")
def delete_employee(
    eid: int,
    db: Session = Depends(get_db),
    user=Depends(require_permission("employee.delete"))
):
    employee = db.query(Employee).filter(Employee.eid == eid).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}
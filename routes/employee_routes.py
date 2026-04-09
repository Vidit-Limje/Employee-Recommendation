# =====================================================
# EMPLOYEE ROUTES (JWT + RBAC + REDIS CACHE)
# =====================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from database.database import get_db
from models.employee import Employee

from utils.dependencies import get_current_user
from utils.permissions import require_permission
from utils.redis_client import redis_client

from schemas.employee_schema import (
    EmployeeResponse,
    EmployeePartialUpdate
)

router = APIRouter(prefix="/employees", tags=["Employees"])


# -----------------------------------------------------
# GET ALL EMPLOYEES (CACHED)
# -----------------------------------------------------

@router.get("/", response_model=list[EmployeeResponse])
def get_all_employees(
    db: Session = Depends(get_db),
    user=Depends(require_permission("employee.read"))
):
    cache_key = "employees:all"

    # 🔍 Try Redis
    cached = redis_client.get(cache_key)
    if cached:
        return json.loads(cached)

    # 🧠 DB fetch
    employees = db.query(Employee).all()

    # ✅ FIX: Use Pydantic schema
    data = [
        EmployeeResponse.model_validate(emp).model_dump()
        for emp in employees
    ]

    # 💾 Store in Redis
    redis_client.setex(cache_key, 300, json.dumps(data))

    return data


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
# UPDATE CURRENT USER PROFILE
# -----------------------------------------------------

@router.patch("/me", response_model=EmployeeResponse)
def update_my_profile(
    updated_data: EmployeePartialUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
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

    # 🔥 CACHE INVALIDATION
    redis_client.delete("employees:all")

    for key in redis_client.scan_iter("project:*:recommendations"):
        redis_client.delete(key)

    return employee


# -----------------------------------------------------
# GET EMPLOYEE BY ID
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
# UPDATE EMPLOYEE BY ID
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

    # 🔥 CACHE INVALIDATION
    redis_client.delete("employees:all")

    for key in redis_client.scan_iter("project:*:recommendations"):
        redis_client.delete(key)

    return employee


# -----------------------------------------------------
# DELETE EMPLOYEE
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

    # 🔥 CACHE INVALIDATION
    redis_client.delete("employees:all")

    for key in redis_client.scan_iter("project:*:recommendations"):
        redis_client.delete(key)

    return {"message": "Employee deleted successfully"}
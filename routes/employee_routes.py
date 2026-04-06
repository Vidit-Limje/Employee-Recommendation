# =====================================================
# EMPLOYEE ROUTES (JWT PROTECTED)
# =====================================================

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.database import get_db
from models.employee import Employee
from utils.dependencies import get_current_user

router = APIRouter(prefix="/employees", tags=["Employees"])


# -----------------------------------------------------
# CREATE EMPLOYEE (OPTIONAL: keep open or restrict)
# -----------------------------------------------------

@router.post("/")
def create_employee(employee_data: dict, db: Session = Depends(get_db)):
    employee = Employee(**employee_data)
    db.add(employee)
    db.commit()
    db.refresh(employee)
    return employee


# -----------------------------------------------------
# GET ALL EMPLOYEES (Protected)
# -----------------------------------------------------

@router.get("/")
def get_all_employees(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(Employee).all()


# -----------------------------------------------------
# GET EMPLOYEE BY ID
# -----------------------------------------------------

@router.get("/{eid}")
def get_employee(
    eid: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    employee = db.query(Employee).filter(Employee.eid == eid).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    return employee


# -----------------------------------------------------
# GET CURRENT LOGGED-IN EMPLOYEE
# -----------------------------------------------------

@router.get("/me")
def get_my_profile(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    eid = user["eid"]

    employee = db.query(Employee).filter(Employee.eid == eid).first()

    return employee


# -----------------------------------------------------
# UPDATE EMPLOYEE
# -----------------------------------------------------

@router.put("/{eid}")
def update_employee(
    eid: int,
    updated_data: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    employee = db.query(Employee).filter(Employee.eid == eid).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    # 🔐 Only allow self-update OR admin
    if user["eid"] != eid and user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Not authorized")

    for key, value in updated_data.items():
        setattr(employee, key, value)

    db.commit()
    db.refresh(employee)

    return employee


# -----------------------------------------------------
# DELETE EMPLOYEE (Admin only)
# -----------------------------------------------------

@router.delete("/{eid}")
def delete_employee(
    eid: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    if user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    employee = db.query(Employee).filter(Employee.eid == eid).first()

    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}
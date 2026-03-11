from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_

from database.database import get_db
from models.employee import Employee

from schemas.employee_schema import (
    EmployeeCreate,
    EmployeeUpdate,
    EmployeePartialUpdate,
    EmployeeResponse
)

router = APIRouter(prefix="/employees", tags=["Employees"])


# CREATE EMPLOYEE
@router.post("/", status_code=201, response_model=EmployeeResponse)
def add_employee(employee: EmployeeCreate, db: Session = Depends(get_db)):

    new_employee = Employee(**employee.model_dump())

    db.add(new_employee)
    db.commit()
    db.refresh(new_employee)

    return new_employee


# GET ALL EMPLOYEES
@router.get("/", response_model=list[EmployeeResponse])
def get_employees(db: Session = Depends(get_db)):

    employees = db.query(Employee).all()

    return employees


# SEARCH EMPLOYEE
@router.get("/search", response_model=list[EmployeeResponse])
def search_employee(query: str, db: Session = Depends(get_db)):

    employees = db.query(Employee).filter(
        or_(
            Employee.firstname.ilike(f"%{query}%"),
            Employee.lastname.ilike(f"%{query}%")
        )
    ).all()

    return employees


# GET EMPLOYEE BY ID
@router.get("/{eid}", response_model=EmployeeResponse)
def get_employee(eid: int, db: Session = Depends(get_db)):

    emp = db.get(Employee, eid)

    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    return emp


# UPDATE EMPLOYEE
@router.put("/{eid}", response_model=EmployeeResponse)
def update_employee(eid: int, employee: EmployeeUpdate, db: Session = Depends(get_db)):

    emp = db.get(Employee, eid)

    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    for key, value in employee.model_dump().items():
        setattr(emp, key, value)

    db.commit()
    db.refresh(emp)

    return emp


# PARTIAL UPDATE
@router.patch("/{eid}", response_model=EmployeeResponse)
def update_employee_partial(eid: int, employee: EmployeePartialUpdate, db: Session = Depends(get_db)):

    emp = db.get(Employee, eid)

    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    update_data = employee.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(emp, key, value)

    db.commit()
    db.refresh(emp)

    return emp


# DELETE EMPLOYEE
@router.delete("/{eid}")
def delete_employee(eid: int, db: Session = Depends(get_db)):

    emp = db.get(Employee, eid)

    if emp is None:
        raise HTTPException(status_code=404, detail="Employee not found")

    db.delete(emp)
    db.commit()

    return {"message": f"Employee {eid} deleted successfully"}
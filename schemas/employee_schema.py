from pydantic import BaseModel
from typing import Optional


# =====================================================
# EMPLOYEE CREATE SCHEMA
# Used when creating a new employee
# =====================================================
class EmployeeCreate(BaseModel):
    firstname: str
    lastname: str
    email: str
    phone: str
    domain: str
    experience: int
    seniority: str
    availability: bool


# =====================================================
# EMPLOYEE UPDATE (FULL UPDATE - PUT)
# Requires all fields
# =====================================================
class EmployeeUpdate(BaseModel):
    firstname: str
    lastname: str
    email: str
    phone: str
    domain: str
    experience: int
    seniority: str
    availability: bool


# =====================================================
# EMPLOYEE PARTIAL UPDATE (PATCH)
# Only updates provided fields
# =====================================================
class EmployeePartialUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    domain: Optional[str] = None
    experience: Optional[int] = None
    seniority: Optional[str] = None
    availability: Optional[bool] = None


# =====================================================
# EMPLOYEE RESPONSE SCHEMA
# Used when returning employee data
# =====================================================
class EmployeeResponse(BaseModel):
    eid: int
    firstname: str
    lastname: str
    email: str
    phone: str
    domain: str
    experience: int
    seniority: str
    availability: bool

    class Config:
        from_attributes = True
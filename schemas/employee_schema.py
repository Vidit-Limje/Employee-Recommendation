from pydantic import BaseModel, EmailStr, Field
from typing import Optional


# =====================================================
# BASE SCHEMA (Reusable)
# =====================================================

class EmployeeBase(BaseModel):
    firstname: str = Field(..., min_length=1, max_length=50)
    lastname: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: str = Field(..., min_length=8, max_length=15)
    domain: str = Field(..., min_length=2, max_length=100)
    experience: int = Field(..., ge=0, le=50)
    seniority: str = Field(..., min_length=2, max_length=50)
    availability: bool


# =====================================================
# EMPLOYEE CREATE SCHEMA
# =====================================================

class EmployeeCreate(EmployeeBase):
    user_id: int = Field(..., gt=0)   # 🔐 Must be valid user


# =====================================================
# EMPLOYEE UPDATE (FULL UPDATE - PUT)
# =====================================================

class EmployeeUpdate(EmployeeBase):
    pass


# =====================================================
# EMPLOYEE PARTIAL UPDATE (PATCH)
# =====================================================

class EmployeePartialUpdate(BaseModel):
    firstname: Optional[str] = Field(None, min_length=1, max_length=50)
    lastname: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=8, max_length=15)
    domain: Optional[str] = Field(None, min_length=2, max_length=100)
    experience: Optional[int] = Field(None, ge=0, le=50)
    seniority: Optional[str] = Field(None, min_length=2, max_length=50)
    availability: Optional[bool] = None


# =====================================================
# EMPLOYEE RESPONSE SCHEMA
# =====================================================

class EmployeeResponse(BaseModel):
    eid: int
    user_id: Optional[int] = None

    firstname: str
    lastname: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    domain: Optional[str] = None
    experience: Optional[int] = None
    seniority: Optional[str] = None
    availability: Optional[bool] = None

    class Config:
        from_attributes = True
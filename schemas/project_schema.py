from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


# =====================================================
# ENUMS (STRONG VALIDATION)
# =====================================================

class PriorityEnum(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class StatusEnum(str, Enum):
    pending = "pending"
    ongoing = "ongoing"
    completed = "completed"


# =====================================================
# BASE SCHEMA (Reusable)
# =====================================================

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    client: str = Field(..., min_length=2, max_length=100)
    domain: str = Field(..., min_length=2, max_length=100)
    priority: PriorityEnum
    status: StatusEnum
    required_experience: int = Field(0, ge=0, le=50)


# =====================================================
# CREATE PROJECT
# =====================================================

class ProjectCreate(ProjectBase):
    pass


# =====================================================
# FULL UPDATE PROJECT (PUT)
# =====================================================

class ProjectUpdate(ProjectBase):
    pass


# =====================================================
# PARTIAL UPDATE PROJECT (PATCH)
# =====================================================

class ProjectPartialUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    client: Optional[str] = Field(None, min_length=2, max_length=100)
    domain: Optional[str] = Field(None, min_length=2, max_length=100)
    priority: Optional[PriorityEnum] = None
    status: Optional[StatusEnum] = None
    required_experience: Optional[int] = Field(None, ge=0, le=50)


# =====================================================
# PROJECT RESPONSE
# =====================================================

class ProjectResponse(ProjectBase):
    pid: int

    class Config:
        from_attributes = True
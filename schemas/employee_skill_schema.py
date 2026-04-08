from pydantic import BaseModel, Field
from typing import Optional


# =====================================================
# BASE SCHEMA (Reusable)
# =====================================================

class EmployeeSkillBase(BaseModel):
    skill_id: int = Field(..., gt=0)
    proficiency_level: int = Field(..., ge=1, le=10)  # 🔥 1–10 scale


# =====================================================
# CREATE SCHEMA
# =====================================================

class EmployeeSkillCreate(EmployeeSkillBase):
    pass


# =====================================================
# PARTIAL UPDATE (OPTIONAL - useful later)
# =====================================================

class EmployeeSkillUpdate(BaseModel):
    proficiency_level: Optional[int] = Field(None, ge=1, le=10)


# =====================================================
# RESPONSE SCHEMA
# =====================================================

class EmployeeSkillResponse(EmployeeSkillBase):
    eid: int = Field(..., gt=0)

    class Config:
        from_attributes = True
from pydantic import BaseModel, Field
from typing import Optional


# =====================================================
# BASE SCHEMA (Reusable)
# =====================================================

class ProjectSkillBase(BaseModel):
    skill_id: int = Field(..., gt=0)
    required_level: int = Field(..., ge=1, le=10)  # 🔥 1–10 scale


# =====================================================
# CREATE SCHEMA
# =====================================================

class ProjectSkillCreate(ProjectSkillBase):
    pass


# =====================================================
# PARTIAL UPDATE (OPTIONAL - useful later)
# =====================================================

class ProjectSkillUpdate(BaseModel):
    required_level: Optional[int] = Field(None, ge=1, le=10)


# =====================================================
# RESPONSE SCHEMA
# =====================================================

class ProjectSkillResponse(ProjectSkillBase):
    pid: int = Field(..., gt=0)

    class Config:
        from_attributes = True
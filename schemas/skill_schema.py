from pydantic import BaseModel, Field
from typing import Optional


# =====================================================
# BASE SCHEMA (Reusable)
# =====================================================

class SkillBase(BaseModel):
    skill_name: str = Field(..., min_length=2, max_length=100)


# =====================================================
# CREATE SCHEMA
# =====================================================

class SkillCreate(SkillBase):
    pass


# =====================================================
# UPDATE SCHEMA (OPTIONAL - useful later)
# =====================================================

class SkillUpdate(BaseModel):
    skill_name: Optional[str] = Field(None, min_length=2, max_length=100)


# =====================================================
# RESPONSE SCHEMA
# =====================================================

class SkillResponse(SkillBase):
    skill_id: int

    class Config:
        from_attributes = True
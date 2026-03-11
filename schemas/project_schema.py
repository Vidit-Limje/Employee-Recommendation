from pydantic import BaseModel
from typing import Optional


# =====================================================
# CREATE PROJECT
# =====================================================
class ProjectCreate(BaseModel):
    name: str
    client: str
    domain: str
    priority: str
    status: str


# =====================================================
# FULL UPDATE PROJECT
# =====================================================
class ProjectUpdate(BaseModel):
    name: str
    client: str
    domain: str
    priority: str
    status: str


# =====================================================
# PARTIAL UPDATE PROJECT
# =====================================================
class ProjectPartialUpdate(BaseModel):
    name: Optional[str] = None
    client: Optional[str] = None
    domain: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None


# =====================================================
# PROJECT RESPONSE
# =====================================================
class ProjectResponse(BaseModel):
    pid: int
    name: str
    client: str
    domain: str
    priority: str
    status: str

    class Config:
        from_attributes = True
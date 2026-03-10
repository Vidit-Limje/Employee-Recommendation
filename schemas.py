from pydantic import BaseModel
from typing import Optional

class EmployeeCreate(BaseModel):
    firstname: str
    lastname: str
    email: str
    phone: str
    domain: str
    experience: int
    seniority: str
    availability: bool


class EmployeeUpdate(BaseModel):
    firstname: str
    lastname: str
    email: str
    phone: str
    domain: str
    experience: int
    seniority: str
    availability: bool

class EmployeePartialUpdate(BaseModel):
    firstname: Optional[str] = None
    lastname: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    domain: Optional[str] = None
    experience: Optional[int] = None
    seniority: Optional[str] = None
    availability: Optional[bool] = None

class ProjectCreate(BaseModel):
    name: str
    client: str
    domain: str
    priority: str
    status: str


class ProjectUpdate(BaseModel):
    name: str
    client: str
    domain: str
    priority: str
    status: str


class ProjectPartialUpdate(BaseModel):
    name: Optional[str] = None
    client: Optional[str] = None
    domain: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
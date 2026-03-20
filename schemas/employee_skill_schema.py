from pydantic import BaseModel


class EmployeeSkillCreate(BaseModel):
    skill_id: int
    proficiency_level: int


class EmployeeSkillResponse(BaseModel):
    eid: int
    skill_id: int
    proficiency_level: int

    class Config:
        from_attributes = True
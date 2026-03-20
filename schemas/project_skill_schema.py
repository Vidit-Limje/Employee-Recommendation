from pydantic import BaseModel


class ProjectSkillBase(BaseModel):
    skill_id: int
    required_level: int


class ProjectSkillCreate(ProjectSkillBase):
    pass


class ProjectSkillResponse(ProjectSkillBase):
    pid: int

    class Config:
        from_attributes = True
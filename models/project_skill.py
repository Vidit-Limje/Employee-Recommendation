from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from models.base import Base

class ProjectSkill(Base):
    __tablename__ = "project_skill"

    pid = Column(Integer, ForeignKey("project.pid"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skill.skill_id"), primary_key=True)
    required_level = Column(Integer, nullable=False)

    # Relationships
    project = relationship("Project", back_populates="skills")
    skill = relationship("Skill")
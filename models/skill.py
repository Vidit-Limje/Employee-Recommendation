from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from models.base import Base


class Skill(Base):
    __tablename__ = "skill"

    skill_id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String, unique=True, nullable=False)

    # 🔗 Relationships

    # Skill ↔ EmployeeSkill (many-to-many via mapping)
    employees = relationship(
        "EmployeeSkill",
        back_populates="skill",
        cascade="all, delete-orphan"
    )

    # Skill ↔ ProjectSkill (many-to-many via mapping)
    projects = relationship(
        "ProjectSkill",
        back_populates="skill",
        cascade="all, delete-orphan"
    )
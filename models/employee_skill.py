from sqlalchemy import Column, Integer, ForeignKey
from models.base import Base
from sqlalchemy.orm import relationship

class EmployeeSkill(Base):
    __tablename__ = "employee_skill"

    eid = Column(
    Integer,
    ForeignKey("employee.eid", ondelete="CASCADE"),
    primary_key=True
)
    skill_id = Column(Integer, ForeignKey("skill.skill_id"), primary_key=True)

    proficiency_level = Column(Integer)

    # ✅ Correct mappings
    employee = relationship("Employee", back_populates="skills")
    skill = relationship("Skill", back_populates="employees")
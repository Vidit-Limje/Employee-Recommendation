from sqlalchemy import Column, Integer, ForeignKey
from models.base import Base


class EmployeeSkill(Base):
    __tablename__ = "employee_skill"

    eid = Column(Integer, ForeignKey("employee.eid"), primary_key=True)
    skill_id = Column(Integer, ForeignKey("skill.skill_id"), primary_key=True)

    proficiency_level = Column(Integer)
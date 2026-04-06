from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from models.base import Base
from sqlalchemy.orm import relationship

class Employee(Base):
    __tablename__ = "employee"

    eid = Column(Integer, primary_key=True, index=True)

    firstname = Column(String)
    lastname = Column(String)
    email = Column(String)
    phone = Column(String)
    domain = Column(String)
    experience = Column(Integer)
    seniority = Column(String)
    availability = Column(Boolean)

    # ✅ NEW
    user_id = Column(Integer, ForeignKey("user_account.user_id"), unique=True)

    user = relationship("UserAccount", back_populates="employee")

    # existing
    skills = relationship("EmployeeSkill", back_populates="employee")
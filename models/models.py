from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base
Base = declarative_base()

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




class Project(Base):
    __tablename__ = "project"

    pid = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    client = Column(String)
    domain = Column(String)
    priority = Column(String)
    status = Column(String) 
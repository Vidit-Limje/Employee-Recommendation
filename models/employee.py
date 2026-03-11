from sqlalchemy import Column, Integer, String, Boolean
from models.base import Base


class Employee(Base):
    """
    Employee table

    Stores employee profile information used for
    project recommendation and workforce management.
    """

    __tablename__ = "employee"

    # Primary Key
    eid = Column(Integer, primary_key=True, index=True)

    # Employee personal information
    firstname = Column(String)
    lastname = Column(String)

    # Contact details
    email = Column(String)
    phone = Column(String)

    # Domain specialization
    # Example: AI, Web, Cloud, Data Science
    domain = Column(String)

    # Years of experience
    experience = Column(Integer)

    # Seniority level
    # Example: Junior, Mid, Senior, Lead
    seniority = Column(String)

    # Availability for project assignment
    availability = Column(Boolean)
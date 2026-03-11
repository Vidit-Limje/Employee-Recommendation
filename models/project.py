from sqlalchemy import Column, Integer, String
from models.base import Base


class Project(Base):
    """
    Project table

    Stores project information used
    to match employees with projects.
    """

    __tablename__ = "project"

    # Primary Key
    pid = Column(Integer, primary_key=True, index=True)

    # Project name
    name = Column(String)

    # Client name
    client = Column(String)

    # Project domain
    # Example: AI, Web, Fintech
    domain = Column(String)

    # Priority level
    # Example: High, Medium, Low
    priority = Column(String)

    # Project status
    # Example: Active, Completed, Planning
    status = Column(String)
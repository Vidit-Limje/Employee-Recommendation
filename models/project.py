from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import relationship
from models.base import Base


class Project(Base):
    __tablename__ = "project"

    pid = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    client = Column(String)
    domain = Column(String)
    priority = Column(String)
    status = Column(String)
    required_experience = Column(Integer, default=0)

    # 🔗 Relationships

    # Project ↔ ProjectSkill (one-to-many)
    skills = relationship(
        "ProjectSkill",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    # Project ↔ ProjectAllocation
    allocations = relationship(
        "ProjectAllocation",
        back_populates="project",
        cascade="all, delete-orphan"
    )

    # Project ↔ Recommendation (optional but useful)
    recommendations = relationship(
        "ProjectRecommendation",
        back_populates="project",
        cascade="all, delete-orphan"
    )
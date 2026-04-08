from sqlalchemy import Column, Integer, String
from models.base import Base

class Permission(Base):
    __tablename__ = "permission"

    permission_id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
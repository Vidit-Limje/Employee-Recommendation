from sqlalchemy import Column, Integer, String, ForeignKey
from models.base import Base

class RolePermission(Base):
    __tablename__ = "role_permission"

    role_name = Column(String, primary_key=True)
    permission_id = Column(Integer, ForeignKey("permission.permission_id"), primary_key=True)
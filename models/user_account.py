# models/user_account.py

from sqlalchemy import Column, Integer, String
from models.base import Base
from sqlalchemy.orm import relationship

class UserAccount(Base):
    __tablename__ = "user_account"

    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="employee")

    # 🔗 Link to employee
    employee = relationship("Employee", back_populates="user", uselist=False)
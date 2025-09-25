from sqlalchemy import Column, Integer, String, JSON
from database import Base

class Users(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, index=True)
    user_name = Column(String, nullable=False)
    user_email = Column(String, unique=True, nullable=False)
    age = Column(Integer, nullable=True)
    ZIP = Column(String, nullable=True)
    recommendations = Column(JSON, nullable=True)

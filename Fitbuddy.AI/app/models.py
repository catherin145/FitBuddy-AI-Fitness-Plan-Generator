
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(80), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)

    goal = Column(String(40), nullable=False)
    intensity = Column(String(20), nullable=False)

    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)
    feedback = Column(Text, nullable=True)

    nutrition_tip = Column(Text, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, index=True)
    email         = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at    = Column(DateTime, default=datetime.utcnow)
    analyses      = relationship("Analysis", back_populates="user", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"
    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    source_type = Column(String(20),  nullable=False)
    source_name = Column(String(500), nullable=True)
    content     = Column(Text,        nullable=False)
    summary     = Column(Text,        nullable=True)
    eli15       = Column(Text,        nullable=True)
    risk_score  = Column(Float,       nullable=True)
    risk_level  = Column(String(20),  nullable=True)
    risks       = Column(JSON,        nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    user        = relationship("User", back_populates="analyses")

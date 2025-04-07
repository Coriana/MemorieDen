# models.py
from sqlalchemy import (
    Column, Integer, String, Text, ForeignKey, DateTime, JSON
)
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, nullable=False)
    meta = Column(JSON, nullable=True)  # Metadata field
    created_at = Column(DateTime, default=datetime.utcnow)
    memories = relationship("Memory", back_populates="user")

class Memory(Base):
    __tablename__ = 'memories'
    id = Column(Integer, primary_key=True)
    memory_id = Column(String, unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    content = Column(Text, nullable=False)
    meta = Column(JSON, nullable=True)  # Metadata field
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="memories")
    history = relationship("History", back_populates="memory")

class History(Base):
    __tablename__ = 'history'
    id = Column(Integer, primary_key=True)
    memory_id = Column(Integer, ForeignKey('memories.id'))
    prev_value = Column(Text, nullable=False)
    new_value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow)
    memory = relationship("Memory", back_populates="history")

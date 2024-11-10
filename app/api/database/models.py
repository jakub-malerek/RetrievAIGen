from sqlalchemy import Column, Integer, String, Text, Boolean, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .db import Base


class ChatSession(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    persona = Column(String, nullable=False)
    closed = Column(Boolean, default=False)
    messages = relationship("Message", back_populates="session")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    role = Column(String, nullable=False)
    content = Column(Text, nullable=False)

    session = relationship("ChatSession", back_populates="messages")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("sessions.id"), nullable=False)
    rating = Column(Integer, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())

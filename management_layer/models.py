from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    is_banned = Column(Boolean, default=False)

    rooms_created = relationship("Room", back_populates="creator")
    messages = relationship("Message", back_populates="sender")
    bans = relationship("RoomBan", back_populates="user")

class Room(Base):
    __tablename__ = "rooms"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    max_participants = Column(Integer, default=10)
    current_participants = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, ForeignKey("users.id"))

    creator = relationship("User", back_populates="rooms_created")
    messages = relationship("Message", back_populates="room")
    bans = relationship("RoomBan", back_populates="room")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))

    room = relationship("Room", back_populates="messages")
    sender = relationship("User", back_populates="messages")

class RoomBan(Base):
    __tablename__ = "room_bans"

    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    reason = Column(String, nullable=True)

    room = relationship("Room", back_populates="bans")
    user = relationship("User", back_populates="bans")

from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    is_banned: bool

    class Config:
        from_attributes = True


class RoomBase(BaseModel):
    name: str
    max_participants: int

class RoomCreate(RoomBase):
    pass

class RoomResponse(RoomBase):
    id: int
    is_active: bool
    created_by: int

    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    content: str

class MessageCreate(MessageBase):
    pass

class MessageResponse(MessageBase):
    id: int
    room_id: int
    user_id: int
    timestamp: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int

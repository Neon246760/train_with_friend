from typing import List, Optional, Union, Dict, Any
from datetime import date
from pydantic import BaseModel

# --- User ---
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    
    class Config:
        from_attributes = True

# --- Friend ---
class FriendCreate(BaseModel):
    friend_username: str

class Friend(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

# --- Training Record ---
class RecordBase(BaseModel):
    date: date
    type: str # 'jogging', 'interval', 'quality'
    details: Dict[str, Any] # 灵活存储

class RecordCreate(RecordBase):
    pass

class Record(RecordBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# --- Token ---
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

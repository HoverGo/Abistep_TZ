from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    balance: float = Field(..., ge=0)


class UserCreate(UserBase):
    pass


class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TransferCreate(BaseModel):
    from_user_id: int
    to_user_id: int
    amount: float = Field(..., gt=0)


class TransferResponse(BaseModel):
    id: int
    from_user_id: int
    to_user_id: int
    amount: float
    created_at: datetime

    class Config:
        from_attributes = True

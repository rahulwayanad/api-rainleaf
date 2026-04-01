from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from models import BookingStatus


# ── Auth ──────────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Contact ───────────────────────────────────────────────────────────────────

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    subject: Optional[str] = None
    message: str

class ContactOut(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    subject: Optional[str]
    message: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Booking ───────────────────────────────────────────────────────────────────

class BookingCreate(BaseModel):
    customer_name: str
    email: EmailStr
    phone: str
    check_in: str
    check_out: str
    guests: int = 2
    villa_id: Optional[int] = None
    special_requests: Optional[str] = None

class BookingStatusUpdate(BaseModel):
    status: BookingStatus

class BookingOut(BaseModel):
    id: int
    customer_name: str
    email: str
    phone: str
    check_in: str
    check_out: str
    guests: int
    villa_id: Optional[int]
    special_requests: Optional[str]
    status: BookingStatus
    created_at: datetime

    class Config:
        from_attributes = True

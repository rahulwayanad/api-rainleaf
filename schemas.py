from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime, date as date_type
from decimal import Decimal
from models import BookingStatus, PaymentStatus


# ── Villa ─────────────────────────────────────────────────────────────────────

class RoomSpec(BaseModel):
    name: str                    # e.g. "Bedroom 1"
    max_guests: int
    is_ac: bool
    has_attached_bathroom: bool

class VillaCreate(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None
    is_active: bool = True
    amenities: List[str] = []
    rooms: List[RoomSpec] = []

class VillaUpdate(VillaCreate):
    pass

class VillaOut(BaseModel):
    id: int
    name: str
    description: Optional[str]
    image_url: Optional[str]
    is_active: bool
    amenities: List[str]
    rooms: List[RoomSpec]
    created_at: datetime

    @field_validator('amenities', mode='before')
    @classmethod
    def amenities_default(cls, v):
        return v or []

    @field_validator('rooms', mode='before')
    @classmethod
    def rooms_default(cls, v):
        return v or []

    class Config:
        from_attributes = True


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
    email: Optional[EmailStr] = None
    phone: str

    @field_validator('email', mode='before')
    @classmethod
    def blank_email_to_none(cls, v):
        return v if v else None
    check_in: str
    check_out: str
    guests: int = 2
    villa_id: Optional[int] = None
    special_requests: Optional[str] = None

class BookingStatusUpdate(BaseModel):
    status: BookingStatus

class BookingPaymentUpdate(BaseModel):
    payment_status:  PaymentStatus
    amount_paid:     Decimal = Decimal('0')
    extra_amount:    Decimal = Decimal('0')
    discount_amount: Decimal = Decimal('0')

class VillaAvailability(BaseModel):
    villa_id: int
    villa_name: str
    available: bool

class BookingOut(BaseModel):
    id: int
    customer_name: str
    email: Optional[str]
    phone: str
    check_in: str
    check_out: str
    guests: int
    villa_id: Optional[int]
    special_requests: Optional[str]
    status: BookingStatus
    payment_status:  PaymentStatus
    amount_paid:     Decimal
    extra_amount:    Decimal
    discount_amount: Decimal
    created_at: datetime

    class Config:
        from_attributes = True


# ── Expense Type ───────────────────────────────────────────────────────────────

class ExpenseTypeCreate(BaseModel):
    name: str

class ExpenseTypeOut(BaseModel):
    id: int
    name: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── Expense ───────────────────────────────────────────────────────────────────

class ExpenseCreate(BaseModel):
    amount: Decimal
    expense_type_id: int
    date: Optional[date_type] = None
    paid_by: Optional[str] = None
    note: Optional[str] = None

class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = None
    expense_type_id: Optional[int] = None
    date: Optional[date_type] = None
    paid_by: Optional[str] = None
    note: Optional[str] = None

class ExpenseOut(BaseModel):
    id: int
    amount: Decimal
    expense_type_id: int
    expense_type_name: Optional[str] = None
    date: date_type
    paid_by: Optional[str]
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

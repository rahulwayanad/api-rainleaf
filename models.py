from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Enum, JSON, Numeric
from sqlalchemy.sql import func
from database import Base
import enum


class BookingStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"

class PaymentStatus(str, enum.Enum):
    not_paid      = "not_paid"
    partially_paid = "partially_paid"
    fully_paid    = "fully_paid"


class Villa(Base):
    __tablename__ = "villas"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    amenities = Column(JSON, nullable=True)   # list of strings
    rooms = Column(JSON, nullable=True)       # list of room objects
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    subject = Column(String(200), nullable=True)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=False)
    check_in = Column(String(20), nullable=False)
    check_out = Column(String(20), nullable=False)
    guests = Column(Integer, nullable=False, default=2)
    villa_id = Column(Integer, nullable=True)   # 1, 2, or 3
    special_requests = Column(Text, nullable=True)
    status = Column(
        Enum(BookingStatus),
        default=BookingStatus.pending,
        nullable=False
    )
    payment_status  = Column(Enum(PaymentStatus), default=PaymentStatus.not_paid, nullable=False)
    amount_paid     = Column(Numeric(10, 2), default=0, nullable=False)
    extra_amount    = Column(Numeric(10, 2), default=0, nullable=False)
    discount_amount = Column(Numeric(10, 2), default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

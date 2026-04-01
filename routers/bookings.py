from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from schemas import BookingCreate, BookingOut, BookingStatusUpdate, BookingPaymentUpdate
from auth import get_current_user
from models import Booking, BookingStatus, User, Villa

router = APIRouter(prefix="/api/bookings", tags=["Bookings"])

BOOKED_STATUSES = [BookingStatus.confirmed, BookingStatus.pending]
VILLA_MAX_GUESTS = 12   # hard cap per villa when rooms aren't configured


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    """Public endpoint — guests submit a booking request.

    If villa_id is provided the booking is validated against that specific villa.
    If villa_id is omitted the system auto-allocates the first free villa in
    ascending ID order whose capacity can fit the requested guest count.
    """

    if payload.check_out <= payload.check_in:
        raise HTTPException(status_code=400, detail="Check-out date must be after check-in date.")

    def _villa_capacity(villa: Villa) -> int:
        rooms = villa.rooms or []
        return sum(r.get("max_guests", 0) for r in rooms) or VILLA_MAX_GUESTS

    def _has_conflict(villa_id: int) -> bool:
        return db.query(Booking).filter(
            Booking.villa_id == villa_id,
            Booking.status.in_(BOOKED_STATUSES),
            Booking.check_in  < payload.check_out,
            Booking.check_out > payload.check_in,
        ).first() is not None

    if payload.villa_id:
        # ── Explicit villa selected by the guest ──────────────────────────────
        villa = db.query(Villa).filter(
            Villa.id == payload.villa_id,
            Villa.is_active,
        ).first()
        if not villa:
            raise HTTPException(status_code=404, detail="Villa not found.")

        if _has_conflict(payload.villa_id):
            raise HTTPException(
                status_code=409,
                detail="This villa is already booked for the selected dates.",
            )

        max_capacity = _villa_capacity(villa)
        if payload.guests > max_capacity:
            raise HTTPException(
                status_code=400,
                detail=f"This villa can accommodate a maximum of {max_capacity} guests.",
            )

        assigned_id = payload.villa_id

    else:
        # ── Auto-allocate: first free villa in ID order ────────────────────────
        booked_ids = {
            row.villa_id
            for row in db.query(Booking.villa_id).filter(
                Booking.status.in_(BOOKED_STATUSES),
                Booking.villa_id.isnot(None),
                Booking.check_in  < payload.check_out,
                Booking.check_out > payload.check_in,
            ).all()
        }

        villas = db.query(Villa).filter(Villa.is_active).order_by(Villa.id).all()
        assigned_villa = None
        for v in villas:
            if v.id in booked_ids:
                continue
            if payload.guests <= _villa_capacity(v):
                assigned_villa = v
                break

        if not assigned_villa:
            raise HTTPException(
                status_code=409,
                detail="No villas available for the selected dates and guest count.",
            )

        assigned_id = assigned_villa.id

    data = payload.model_dump()
    data["villa_id"] = assigned_id
    booking = Booking(**data)
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("", response_model=List[BookingOut])
def list_bookings(
    skip: int = 0,
    limit: int = 50,
    status: Optional[BookingStatus] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Admin only — list all bookings, optionally filtered by status."""
    query = db.query(Booking)
    if status:
        query = query.filter(Booking.status == status)
    return query.order_by(Booking.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{booking_id}", response_model=BookingOut)
def get_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Admin only — get a single booking's full details."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return booking


@router.patch("/{booking_id}/status", response_model=BookingOut)
def update_booking_status(
    booking_id: int,
    payload: BookingStatusUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Admin only — confirm or cancel a booking."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.status = payload.status
    db.commit()
    db.refresh(booking)
    return booking


@router.patch("/{booking_id}/payment", response_model=BookingOut)
def update_booking_payment(
    booking_id: int,
    payload: BookingPaymentUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Admin only — update payment details for a booking."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    booking.payment_status  = payload.payment_status
    booking.amount_paid     = payload.amount_paid
    booking.extra_amount    = payload.extra_amount
    booking.discount_amount = payload.discount_amount
    db.commit()
    db.refresh(booking)
    return booking


@router.delete("/{booking_id}", status_code=204)
def delete_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Admin only — delete a booking record."""
    booking = db.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    db.delete(booking)
    db.commit()

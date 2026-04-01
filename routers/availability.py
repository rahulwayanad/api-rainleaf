from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import date, timedelta
import calendar as cal_module
from database import get_db
from schemas import VillaAvailability
from models import Booking, BookingStatus, Villa

VILLA_MAX_GUESTS = 12   # default cap when no rooms are configured

router = APIRouter(prefix="/api/availability", tags=["Availability"])


@router.get("", response_model=List[VillaAvailability])
def check_availability(
    check_in: str = Query(..., description="YYYY-MM-DD"),
    check_out: str = Query(..., description="YYYY-MM-DD"),
    guests: int = Query(1),
    db: Session = Depends(get_db),
):
    """Public — which villas are free for the given date range and guest count.

    A villa is considered occupied if it has ANY pending/confirmed booking that
    overlaps the requested dates.  Capacity defaults to 12 when rooms are not
    yet configured.
    """
    booked = db.query(Booking.villa_id).filter(
        Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
        Booking.villa_id.isnot(None),
        Booking.check_in < check_out,
        Booking.check_out > check_in,
    ).all()
    booked_ids = {row.villa_id for row in booked}
    villas = db.query(Villa).filter(Villa.is_active).order_by(Villa.id).all()

    result = []
    for v in villas:
        rooms = v.rooms or []
        capacity = sum(r.get("max_guests", 0) for r in rooms) or VILLA_MAX_GUESTS
        fits = guests <= capacity
        result.append(VillaAvailability(
            villa_id=v.id,
            villa_name=v.name,
            available=v.id not in booked_ids and fits,
        ))
    return result


@router.get("/calendar")
def availability_calendar(
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
):
    """Public — day-by-day villa availability for a full month."""
    first_day = date(year, month, 1)
    last_day  = date(year, month, cal_module.monthrange(year, month)[1])

    bookings = db.query(Booking).filter(
        Booking.status.in_([BookingStatus.confirmed, BookingStatus.pending]),
        Booking.villa_id.isnot(None),
        Booking.check_in  <= str(last_day),
        Booking.check_out >  str(first_day),
    ).all()

    villas = db.query(Villa).filter(Villa.is_active == True).order_by(Villa.id).all()

    # Build {date_str: [villa_id, ...]} for every booked day in the month
    booked_days: dict[str, list] = {}
    for b in bookings:
        try:
            ci = date.fromisoformat(b.check_in)
            co = date.fromisoformat(b.check_out)
        except ValueError:
            continue
        current = max(ci, first_day)
        end     = min(co, last_day + timedelta(days=1))
        while current < end:
            key = str(current)
            if key not in booked_days:
                booked_days[key] = []
            if b.villa_id not in booked_days[key]:
                booked_days[key].append(b.villa_id)
            current += timedelta(days=1)

    return {
        "villas":     [{"id": v.id, "name": v.name} for v in villas],
        "booked_days": booked_days,
    }

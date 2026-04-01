from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import VillaCreate, VillaUpdate, VillaOut
from auth import get_current_user
from models import Villa, User

router = APIRouter(prefix="/api/villas", tags=["Villas"])


@router.get("", response_model=List[VillaOut])
def list_villas(db: Session = Depends(get_db)):
    """Public — list all active villas."""
    return db.query(Villa).filter(Villa.is_active == True).order_by(Villa.id).all()


@router.get("/all", response_model=List[VillaOut])
def list_all_villas(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    """Admin — list all villas including inactive."""
    return db.query(Villa).order_by(Villa.id).all()


@router.post("", response_model=VillaOut, status_code=201)
def create_villa(
    payload: VillaCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    villa = Villa(
        name=payload.name,
        description=payload.description,
        image_url=payload.image_url,
        is_active=payload.is_active,
        amenities=payload.amenities,
        rooms=[r.model_dump() for r in payload.rooms],
    )
    db.add(villa)
    db.commit()
    db.refresh(villa)
    return villa


@router.put("/{villa_id}", response_model=VillaOut)
def update_villa(
    villa_id: int,
    payload: VillaUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    villa = db.query(Villa).filter(Villa.id == villa_id).first()
    if not villa:
        raise HTTPException(status_code=404, detail="Villa not found")
    villa.name = payload.name
    villa.description = payload.description
    villa.image_url = payload.image_url
    villa.is_active = payload.is_active
    villa.amenities = payload.amenities
    villa.rooms = [r.model_dump() for r in payload.rooms]
    db.commit()
    db.refresh(villa)
    return villa


@router.delete("/{villa_id}", status_code=204)
def delete_villa(
    villa_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    villa = db.query(Villa).filter(Villa.id == villa_id).first()
    if not villa:
        raise HTTPException(status_code=404, detail="Villa not found")
    db.delete(villa)
    db.commit()

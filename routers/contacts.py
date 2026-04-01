from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from database import get_db
from schemas import ContactCreate, ContactOut
from auth import get_current_user
import models

router = APIRouter(prefix="/api/contacts", tags=["Contacts"])


@router.post("", response_model=ContactOut, status_code=201)
def submit_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    """Public endpoint — anyone can submit a contact message."""
    contact = models.Contact(**payload.model_dump())
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("", response_model=List[ContactOut])
def list_contacts(
    skip: int = 0,
    limit: int = 50,
    unread_only: bool = False,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Admin only — list all contact submissions."""
    query = db.query(models.Contact)
    if unread_only:
        query = query.filter(models.Contact.is_read == False)
    return query.order_by(models.Contact.created_at.desc()).offset(skip).limit(limit).all()


@router.patch("/{contact_id}/read", response_model=ContactOut)
def mark_as_read(
    contact_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Admin only — mark a contact message as read."""
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    contact.is_read = True
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=204)
def delete_contact(
    contact_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    """Admin only — delete a contact message."""
    contact = db.query(models.Contact).filter(models.Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    db.delete(contact)
    db.commit()

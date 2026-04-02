from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from database import get_db
from schemas import ExpenseCreate, ExpenseUpdate, ExpenseOut, ExpenseTypeCreate, ExpenseTypeOut
from auth import get_current_user
from models import Expense, ExpenseType, User

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])


# ── Expense Types ──────────────────────────────────────────────────────────────

@router.get("/types", response_model=List[ExpenseTypeOut])
def list_expense_types(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(ExpenseType).order_by(ExpenseType.name).all()


@router.post("/types", response_model=ExpenseTypeOut)
def create_expense_type(payload: ExpenseTypeCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    existing = db.query(ExpenseType).filter(ExpenseType.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Expense type already exists")
    et = ExpenseType(name=payload.name)
    db.add(et)
    db.commit()
    db.refresh(et)
    return et


@router.delete("/types/{type_id}")
def delete_expense_type(type_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    et = db.query(ExpenseType).filter(ExpenseType.id == type_id).first()
    if not et:
        raise HTTPException(status_code=404, detail="Expense type not found")
    db.delete(et)
    db.commit()
    return {"detail": "Deleted"}


# ── Expenses ───────────────────────────────────────────────────────────────────

@router.get("", response_model=List[ExpenseOut])
def list_expenses(
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    expense_type_id: Optional[int] = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Expense)
    if from_date:
        q = q.filter(Expense.date >= from_date)
    if to_date:
        q = q.filter(Expense.date <= to_date)
    if expense_type_id:
        q = q.filter(Expense.expense_type_id == expense_type_id)
    expenses = q.order_by(Expense.date.desc()).all()

    result = []
    for e in expenses:
        et = db.query(ExpenseType).filter(ExpenseType.id == e.expense_type_id).first()
        out = ExpenseOut.model_validate(e)
        out.expense_type_name = et.name if et else None
        result.append(out)
    return result


@router.post("", response_model=ExpenseOut)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    et = db.query(ExpenseType).filter(ExpenseType.id == payload.expense_type_id).first()
    if not et:
        raise HTTPException(status_code=404, detail="Expense type not found")
    expense = Expense(
        amount=payload.amount,
        expense_type_id=payload.expense_type_id,
        date=payload.date or date.today(),
        paid_by=payload.paid_by,
        note=payload.note,
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    out = ExpenseOut.model_validate(expense)
    out.expense_type_name = et.name
    return out


@router.patch("/{expense_id}", response_model=ExpenseOut)
def update_expense(expense_id: int, payload: ExpenseUpdate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    et = db.query(ExpenseType).filter(ExpenseType.id == expense.expense_type_id).first()
    out = ExpenseOut.model_validate(expense)
    out.expense_type_name = et.name if et else None
    return out


@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.delete(expense)
    db.commit()
    return {"detail": "Deleted"}

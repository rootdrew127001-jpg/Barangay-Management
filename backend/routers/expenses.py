from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from ..models import Expense, TransactionLedger
from ..schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from ..database import get_db

router = APIRouter(prefix="/api/expenses", tags=["expenses"])

@router.post("", response_model=ExpenseResponse)
def create_expense(expense: ExpenseCreate, db: Session = Depends(get_db)):
    db_expense = Expense(**expense.dict())
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)

    balance = db.query(TransactionLedger).order_by(TransactionLedger.id.desc()).first()
    running_balance = balance.running_balance if balance else 0
    running_balance -= expense.amount

    ledger = TransactionLedger(
        transaction_type="expense",
        transaction_id=db_expense.id,
        date=expense.date,
        description=f"Expense: {expense.category}",
        debit_amount=expense.amount,
        running_balance=running_balance,
    )
    db.add(ledger)
    db.commit()
    return db_expense

@router.get("", response_model=List[ExpenseResponse])
def list_expenses(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Expense)
    if start_date:
        query = query.filter(Expense.date >= start_date)
    if end_date:
        query = query.filter(Expense.date <= end_date)
    if category:
        query = query.filter(Expense.category == category)
    return query.offset(skip).limit(limit).all()

@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(expense_id: int, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense

@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(expense_id: int, expense: ExpenseUpdate, db: Session = Depends(get_db)):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")

    for field, value in expense.dict(exclude_unset=True).items():
        setattr(db_expense, field, value)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.delete("/{expense_id}")
def delete_expense(expense_id: int, db: Session = Depends(get_db)):
    db_expense = db.query(Expense).filter(Expense.id == expense_id).first()
    if not db_expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    db.query(TransactionLedger).filter(
        TransactionLedger.transaction_type == "expense",
        TransactionLedger.transaction_id == expense_id
    ).delete()
    db.delete(db_expense)
    db.commit()
    return {"message": "Expense deleted"}

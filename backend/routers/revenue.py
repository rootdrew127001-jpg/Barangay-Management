from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date
from typing import List, Optional
from ..models import Revenue, TransactionLedger
from ..schemas import RevenueCreate, RevenueUpdate, RevenueResponse
from ..database import get_db

router = APIRouter(prefix="/api/revenue", tags=["revenue"])

@router.post("", response_model=RevenueResponse)
def create_revenue(revenue: RevenueCreate, db: Session = Depends(get_db)):
    db_revenue = Revenue(**revenue.dict())
    db.add(db_revenue)
    db.commit()
    db.refresh(db_revenue)

    balance = db.query(TransactionLedger).order_by(TransactionLedger.id.desc()).first()
    running_balance = balance.running_balance if balance else 0
    running_balance += revenue.amount

    ledger = TransactionLedger(
        transaction_type="revenue",
        transaction_id=db_revenue.id,
        date=revenue.date,
        description=f"Revenue: {revenue.source_type}",
        credit_amount=revenue.amount,
        running_balance=running_balance,
    )
    db.add(ledger)
    db.commit()
    return db_revenue

@router.get("", response_model=List[RevenueResponse])
def list_revenues(
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Revenue)
    if start_date:
        query = query.filter(Revenue.date >= start_date)
    if end_date:
        query = query.filter(Revenue.date <= end_date)
    if status:
        query = query.filter(Revenue.payment_status == status)
    return query.offset(skip).limit(limit).all()

@router.get("/{revenue_id}", response_model=RevenueResponse)
def get_revenue(revenue_id: int, db: Session = Depends(get_db)):
    revenue = db.query(Revenue).filter(Revenue.id == revenue_id).first()
    if not revenue:
        raise HTTPException(status_code=404, detail="Revenue not found")
    return revenue

@router.put("/{revenue_id}", response_model=RevenueResponse)
def update_revenue(revenue_id: int, revenue: RevenueUpdate, db: Session = Depends(get_db)):
    db_revenue = db.query(Revenue).filter(Revenue.id == revenue_id).first()
    if not db_revenue:
        raise HTTPException(status_code=404, detail="Revenue not found")

    for field, value in revenue.dict(exclude_unset=True).items():
        setattr(db_revenue, field, value)
    db.commit()
    db.refresh(db_revenue)
    return db_revenue

@router.delete("/{revenue_id}")
def delete_revenue(revenue_id: int, db: Session = Depends(get_db)):
    db_revenue = db.query(Revenue).filter(Revenue.id == revenue_id).first()
    if not db_revenue:
        raise HTTPException(status_code=404, detail="Revenue not found")
    db.query(TransactionLedger).filter(
        TransactionLedger.transaction_type == "revenue",
        TransactionLedger.transaction_id == revenue_id
    ).delete()
    db.delete(db_revenue)
    db.commit()
    return {"message": "Revenue deleted"}
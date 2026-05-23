from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract
from datetime import date
from ..models import Revenue, Expense
from ..schemas import ReportSummary
from ..database import get_db

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/monthly", response_model=ReportSummary)
def get_monthly_report(month: int, year: int, db: Session = Depends(get_db)):
    revenue = db.query(Revenue).filter(
        extract('month', Revenue.date) == month,
        extract('year', Revenue.date) == year
    ).all()
    expense = db.query(Expense).filter(
        extract('month', Expense.date) == month,
        extract('year', Expense.date) == year
    ).all()

    total_revenue = sum(r.amount for r in revenue)
    total_expense = sum(e.amount for e in expense)
    return ReportSummary(
        total_revenue=total_revenue,
        total_expenses=total_expense,
        net_balance=total_revenue - total_expense,
        month=month,
        year=year
    )

@router.get("/quarterly", response_model=ReportSummary)
def get_quarterly_report(quarter: int, year: int, db: Session = Depends(get_db)):
    months = {
        1: (1, 2, 3),
        2: (4, 5, 6),
        3: (7, 8, 9),
        4: (10, 11, 12),
    }
    if quarter not in months:
        raise HTTPException(status_code=400, detail="Invalid quarter (1-4)")

    revenue = db.query(Revenue).filter(
        extract('month', Revenue.date).in_(months[quarter]),
        extract('year', Revenue.date) == year
    ).all()
    expense = db.query(Expense).filter(
        extract('month', Expense.date).in_(months[quarter]),
        extract('year', Expense.date) == year
    ).all()

    total_revenue = sum(r.amount for r in revenue)
    total_expense = sum(e.amount for e in expense)
    return ReportSummary(
        total_revenue=total_revenue,
        total_expenses=total_expense,
        net_balance=total_revenue - total_expense,
        month=quarter,
        year=year
    )

@router.get("/annual", response_model=ReportSummary)
def get_annual_report(year: int, db: Session = Depends(get_db)):
    revenue = db.query(Revenue).filter(extract('year', Revenue.date) == year).all()
    expense = db.query(Expense).filter(extract('year', Expense.date) == year).all()

    total_revenue = sum(r.amount for r in revenue)
    total_expense = sum(e.amount for e in expense)
    return ReportSummary(
        total_revenue=total_revenue,
        total_expenses=total_expense,
        net_balance=total_revenue - total_expense,
        year=year
    )

@router.get("/summary", response_model=ReportSummary)
def get_summary(db: Session = Depends(get_db)):
    revenue = db.query(Revenue).all()
    expense = db.query(Expense).all()

    total_revenue = sum(r.amount for r in revenue)
    total_expense = sum(e.amount for e in expense)
    return ReportSummary(
        total_revenue=total_revenue,
        total_expenses=total_expense,
        net_balance=total_revenue - total_expense
    )

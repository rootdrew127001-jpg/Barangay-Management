from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict
from ..models import TransactionLedger
from ..schemas import TransactionLedgerResponse
from ..database import get_db
from io import StringIO
import csv

router = APIRouter(prefix="/api/transactions", tags=["transactions"])

@router.get("", response_model=List[TransactionLedgerResponse])
def get_ledger(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return db.query(TransactionLedger).order_by(TransactionLedger.date).offset(skip).limit(limit).all()

@router.get("/export-csv")
def export_transactions(db: Session = Depends(get_db)):
    transactions = db.query(TransactionLedger).order_by(TransactionLedger.date).all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Date", "Type", "Description", "Debit", "Credit", "Balance"])

    for t in transactions:
        writer.writerow([
            t.date,
            t.transaction_type,
            t.description,
            t.debit_amount if t.debit_amount > 0 else "",
            t.credit_amount if t.credit_amount > 0 else "",
            t.running_balance
        ])

    return {
        "filename": "transactions.csv",
        "content": output.getvalue()
    }

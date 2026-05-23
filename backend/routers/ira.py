from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models import IRAAllocation
from ..schemas import IRAAllocationCreate, IRAAllocationUpdate, IRAAllocationResponse
from ..database import get_db

router = APIRouter(prefix="/api/ira", tags=["ira"])

@router.get("", response_model=IRAAllocationResponse)
def get_current_ira(db: Session = Depends(get_db)):
    from datetime import date
    today = date.today()
    ira = db.query(IRAAllocation).filter(
        IRAAllocation.month == today.month,
        IRAAllocation.year == today.year
    ).first()
    if not ira:
        raise HTTPException(status_code=404, detail="IRA allocation not found")
    return ira

@router.post("", response_model=IRAAllocationResponse)
def create_or_update_ira(ira: IRAAllocationCreate, db: Session = Depends(get_db)):
    existing = db.query(IRAAllocation).filter(
        IRAAllocation.month == ira.month,
        IRAAllocation.year == ira.year
    ).first()

    if existing:
        for field, value in ira.dict().items():
            setattr(existing, field, value)
        db.commit()
        db.refresh(existing)
        return existing

    db_ira = IRAAllocation(**ira.dict())
    db.add(db_ira)
    db.commit()
    db.refresh(db_ira)
    return db_ira

@router.get("/history", response_model=List[IRAAllocationResponse])
def get_ira_history(year: int = None, db: Session = Depends(get_db)):
    query = db.query(IRAAllocation)
    if year:
        query = query.filter(IRAAllocation.year == year)
    return query.all()

@router.put("/{ira_id}", response_model=IRAAllocationResponse)
def update_ira(ira_id: int, ira: IRAAllocationUpdate, db: Session = Depends(get_db)):
    db_ira = db.query(IRAAllocation).filter(IRAAllocation.id == ira_id).first()
    if not db_ira:
        raise HTTPException(status_code=404, detail="IRA allocation not found")

    for field, value in ira.dict(exclude_unset=True).items():
        setattr(db_ira, field, value)
    db.commit()
    db.refresh(db_ira)
    return db_ira

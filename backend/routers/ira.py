from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from ..models import IRAAllocation, IRAAllocationDetail, Revenue
from ..schemas import (
    IRAAllocationCreate, IRAAllocationUpdate, IRAAllocationResponse,
    IRAAllocationDetailCreate, IRAAllocationDetailUpdate, IRAAllocationDetailResponse
)
from ..database import get_db
from sqlalchemy import extract, func
from datetime import date

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

@router.get("/{ira_id}/details", response_model=List[IRAAllocationDetailResponse])
def get_allocation_details(ira_id: int, db: Session = Depends(get_db)):
    ira = db.query(IRAAllocation).filter(IRAAllocation.id == ira_id).first()
    if not ira:
        raise HTTPException(status_code=404, detail="IRA allocation not found")
    
    details = db.query(IRAAllocationDetail).filter(
        IRAAllocationDetail.ira_id == ira_id
    ).all()
    return details

@router.post("/{ira_id}/details", response_model=IRAAllocationDetailResponse)
def add_allocation_detail(
    ira_id: int,
    detail: IRAAllocationDetailCreate,
    db: Session = Depends(get_db)
):
    ira = db.query(IRAAllocation).filter(IRAAllocation.id == ira_id).first()
    if not ira:
        raise HTTPException(status_code=404, detail="IRA allocation not found")
    
    existing_total = db.query(func.sum(IRAAllocationDetail.amount)).filter(
        IRAAllocationDetail.ira_id == ira_id
    ).scalar() or 0
    
    if existing_total + detail.amount > ira.total_ira:
        raise HTTPException(
            status_code=400,
            detail=f"Total allocation exceeds IRA budget. Remaining: ₱{ira.total_ira - existing_total}"
        )
    
    db_detail = IRAAllocationDetail(ira_id=ira_id, **detail.dict())
    db.add(db_detail)
    db.commit()
    db.refresh(db_detail)
    return db_detail

@router.put("/{ira_id}/details/{detail_id}", response_model=IRAAllocationDetailResponse)
def update_allocation_detail(
    ira_id: int,
    detail_id: int,
    detail: IRAAllocationDetailUpdate,
    db: Session = Depends(get_db)
):
    db_detail = db.query(IRAAllocationDetail).filter(
        IRAAllocationDetail.id == detail_id,
        IRAAllocationDetail.ira_id == ira_id
    ).first()
    if not db_detail:
        raise HTTPException(status_code=404, detail="Allocation detail not found")
    
    if detail.amount is not None:
        ira = db.query(IRAAllocation).filter(IRAAllocation.id == ira_id).first()
        existing_total = db.query(func.sum(IRAAllocationDetail.amount)).filter(
            IRAAllocationDetail.ira_id == ira_id,
            IRAAllocationDetail.id != detail_id
        ).scalar() or 0
        
        if existing_total + detail.amount > ira.total_ira:
            raise HTTPException(
                status_code=400,
                detail=f"Total allocation exceeds IRA budget. Remaining: ₱{ira.total_ira - existing_total}"
            )
    
    for field, value in detail.dict(exclude_unset=True).items():
        setattr(db_detail, field, value)
    db.commit()
    db.refresh(db_detail)
    return db_detail

@router.delete("/{ira_id}/details/{detail_id}")
def delete_allocation_detail(ira_id: int, detail_id: int, db: Session = Depends(get_db)):
    db_detail = db.query(IRAAllocationDetail).filter(
        IRAAllocationDetail.id == detail_id,
        IRAAllocationDetail.ira_id == ira_id
    ).first()
    if not db_detail:
        raise HTTPException(status_code=404, detail="Allocation detail not found")
    
    db.delete(db_detail)
    db.commit()
    return {"message": "Allocation detail deleted successfully"}

@router.get("/calculate/{month}/{year}")
def calculate_ira_from_revenue(month: int, year: int, db: Session = Depends(get_db)):
    """Calculate IRA as 20% of total revenue for the given month/year"""
    
    revenue = db.query(Revenue).filter(
        extract('month', Revenue.date) == month,
        extract('year', Revenue.date) == year
    ).all()
    
    total_revenue = sum(r.amount for r in revenue)
    ira_amount = total_revenue * 0.20  
    
    existing_ira = db.query(IRAAllocation).filter(
        IRAAllocation.month == month,
        IRAAllocation.year == year
    ).first()
    
    if existing_ira:
        existing_ira.total_ira = ira_amount
        db.commit()
        db.refresh(existing_ira)
        return {
            "total_revenue": total_revenue,
            "ira_amount": ira_amount,
            "ira_allocation": existing_ira
        }
    else:
        new_ira = IRAAllocation(
            month=month,
            year=year,
            total_ira=ira_amount,
            utilization_status="active"
        )
        db.add(new_ira)
        db.commit()
        db.refresh(new_ira)
        return {
            "total_revenue": total_revenue,
            "ira_amount": ira_amount,
            "ira_allocation": new_ira
        }


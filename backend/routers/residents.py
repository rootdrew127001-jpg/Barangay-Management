from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..database import get_db
from ..models import Resident
from ..schemas import ResidentCreate, ResidentUpdate, ResidentResponse
from typing import List

router = APIRouter(prefix="/residents", tags=["residents"])

def generate_resident_id(db: Session) -> str:
    count = db.query(Resident).count()
    return f"RES-{str(count + 1).zfill(3)}"

@router.post("/", response_model=ResidentResponse)
def create_resident(resident: ResidentCreate, db: Session = Depends(get_db)):
    resident_id = generate_resident_id(db)
    db_resident = Resident(
        resident_id=resident_id,
        full_name=resident.full_name,
        address=resident.address,
        contact_number=resident.contact_number,
        status=resident.status
    )
    db.add(db_resident)
    db.commit()
    db.refresh(db_resident)
    return db_resident

@router.get("/", response_model=List[ResidentResponse])
def list_residents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    residents = db.query(Resident).order_by(desc(Resident.created_at)).offset(skip).limit(limit).all()
    return residents

@router.get("/{resident_id}", response_model=ResidentResponse)
def get_resident(resident_id: int, db: Session = Depends(get_db)):
    resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    return resident

@router.put("/{resident_id}", response_model=ResidentResponse)
def update_resident(resident_id: int, resident_update: ResidentUpdate, db: Session = Depends(get_db)):
    db_resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not db_resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    
    update_data = resident_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_resident, key, value)
    
    db.add(db_resident)
    db.commit()
    db.refresh(db_resident)
    return db_resident

@router.delete("/{resident_id}")
def delete_resident(resident_id: int, db: Session = Depends(get_db)):
    db_resident = db.query(Resident).filter(Resident.id == resident_id).first()
    if not db_resident:
        raise HTTPException(status_code=404, detail="Resident not found")
    
    db.delete(db_resident)
    db.commit()
    return {"message": "Resident deleted successfully"}

@router.get("/search/by-name/", response_model=List[ResidentResponse])
def search_residents(query: str, db: Session = Depends(get_db)):
    residents = db.query(Resident).filter(
        (Resident.full_name.ilike(f"%{query}%")) | 
        (Resident.address.ilike(f"%{query}%"))
    ).all()
    return residents

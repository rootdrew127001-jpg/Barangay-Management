from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password_hash = Column(String)
    role = Column(String, default="treasurer")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Revenue(Base):
    __tablename__ = "revenue"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    source_type = Column(String)
    amount = Column(Float)
    or_number = Column(String, nullable=True)
    payment_status = Column(String, default="pending")
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    category = Column(String)
    amount = Column(Float)
    description = Column(String)
    status = Column(String, default="recorded")
    created_at = Column(DateTime, default=datetime.utcnow)

class IRAAllocation(Base):
    __tablename__ = "ira_allocation"

    id = Column(Integer, primary_key=True, index=True)
    month = Column(Integer)
    year = Column(Integer)
    total_ira = Column(Float)
    infrastructure_percent = Column(Float, default=40)
    health_percent = Column(Float, default=20)
    education_percent = Column(Float, default=12)
    other_percent = Column(Float, default=28)
    utilization_status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)

class TransactionLedger(Base):
    __tablename__ = "transaction_ledger"

    id = Column(Integer, primary_key=True, index=True)
    transaction_type = Column(String)
    transaction_id = Column(Integer)
    date = Column(Date, index=True)
    description = Column(String)
    debit_amount = Column(Float, default=0)
    credit_amount = Column(Float, default=0)
    running_balance = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class Resident(Base):
    __tablename__ = "residents"

    id = Column(Integer, primary_key=True, index=True)
    resident_id = Column(String, unique=True, index=True)
    full_name = Column(String, index=True)
    address = Column(String)
    contact_number = Column(String, nullable=True)
    status = Column(String, default="Active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

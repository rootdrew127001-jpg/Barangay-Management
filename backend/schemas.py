from pydantic import BaseModel
from datetime import date as date_type, datetime
from typing import Optional

class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "treasurer"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class RevenueCreate(BaseModel):
    date: date_type
    source_type: str
    amount: float
    or_number: Optional[str] = None
    payment_status: str = "pending"
    notes: Optional[str] = None

class RevenueUpdate(BaseModel):
    date: Optional[date_type] = None
    source_type: Optional[str] = None
    amount: Optional[float] = None
    or_number: Optional[str] = None
    payment_status: Optional[str] = None
    notes: Optional[str] = None

class RevenueResponse(BaseModel):
    id: int
    date: date_type
    source_type: str
    amount: float
    or_number: Optional[str]
    payment_status: str
    notes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ExpenseCreate(BaseModel):
    date: date_type
    category: str
    amount: float
    description: str
    status: str = "recorded"

class ExpenseUpdate(BaseModel):
    date: Optional[date_type] = None
    category: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ExpenseResponse(BaseModel):
    id: int
    date: date_type
    category: str
    amount: float
    description: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True

class IRAAllocationCreate(BaseModel):
    month: int
    year: int
    total_ira: float
    infrastructure_percent: float = 40
    health_percent: float = 20
    education_percent: float = 12
    other_percent: float = 28

class IRAAllocationUpdate(BaseModel):
    total_ira: Optional[float] = None
    infrastructure_percent: Optional[float] = None
    health_percent: Optional[float] = None
    education_percent: Optional[float] = None
    other_percent: Optional[float] = None

class IRAAllocationResponse(BaseModel):
    id: int
    month: int
    year: int
    total_ira: float
    infrastructure_percent: float
    health_percent: float
    education_percent: float
    other_percent: float
    utilization_status: str
    created_at: datetime

    class Config:
        from_attributes = True

class IRAAllocationDetailCreate(BaseModel):
    category_name: str
    amount: float
    description: Optional[str] = None

class IRAAllocationDetailUpdate(BaseModel):
    category_name: Optional[str] = None
    amount: Optional[float] = None
    description: Optional[str] = None

class IRAAllocationDetailResponse(BaseModel):
    id: int
    ira_id: int
    category_name: str
    amount: float
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TransactionLedgerResponse(BaseModel):
    id: int
    transaction_type: str
    transaction_id: int
    date: date_type
    description: str
    debit_amount: float
    credit_amount: float
    running_balance: float
    created_at: datetime

    class Config:
        from_attributes = True

class LoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    token: str
    user: UserResponse

class ReportSummary(BaseModel):
    total_revenue: float
    total_expenses: float
    net_balance: float
    month: Optional[int] = None
    year: Optional[int] = None

class ResidentCreate(BaseModel):
    full_name: str
    address: str
    contact_number: Optional[str] = None
    status: str = "Active"

class ResidentUpdate(BaseModel):
    full_name: Optional[str] = None
    address: Optional[str] = None
    contact_number: Optional[str] = None
    status: Optional[str] = None

class ResidentResponse(BaseModel):
    id: int
    resident_id: str
    full_name: str
    address: str
    contact_number: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

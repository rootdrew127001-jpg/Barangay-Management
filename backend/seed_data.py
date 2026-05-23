from datetime import date, datetime, timedelta
import hashlib
from .database import SessionLocal, engine
from .models import Base, User, Revenue, Expense, IRAAllocation, TransactionLedger

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(User).first() is not None:
        print("Database already seeded.")
        return

    users = [
        User(username="admin", password_hash=get_password_hash("admin123"), role="admin"),
        User(username="treasurer", password_hash=get_password_hash("treasurer123"), role="treasurer"),
    ]
    db.add_all(users)
    db.commit()

    today = date.today()
    revenue_data = [
        Revenue(date=today - timedelta(days=30), source_type="certificate", amount=500, or_number="OR-001", payment_status="paid"),
        Revenue(date=today - timedelta(days=28), source_type="community_tax", amount=1200, or_number="OR-002", payment_status="paid"),
        Revenue(date=today - timedelta(days=25), source_type="clearance", amount=300, or_number="OR-003", payment_status="pending"),
        Revenue(date=today - timedelta(days=20), source_type="building_permit", amount=800, or_number="OR-004", payment_status="paid"),
        Revenue(date=today - timedelta(days=15), source_type="certificate", amount=450, or_number="OR-005", payment_status="paid"),
        Revenue(date=today - timedelta(days=10), source_type="community_tax", amount=1100, or_number="OR-006", payment_status="paid"),
        Revenue(date=today - timedelta(days=5), source_type="clearance", amount=350, or_number="OR-007", payment_status="paid"),
        Revenue(date=today, source_type="certificate", amount=550, or_number="OR-008", payment_status="pending"),
    ]
    db.add_all(revenue_data)
    db.commit()

    expense_data = [
        Expense(date=today - timedelta(days=30), category="utilities", amount=2000, description="Electric bill"),
        Expense(date=today - timedelta(days=25), category="supplies", amount=500, description="Office supplies"),
        Expense(date=today - timedelta(days=20), category="maintenance", amount=1500, description="Building maintenance"),
        Expense(date=today - timedelta(days=15), category="streetlight", amount=800, description="Streetlight repair"),
        Expense(date=today - timedelta(days=10), category="utilities", amount=2100, description="Water bill"),
        Expense(date=today - timedelta(days=5), category="supplies", amount=400, description="Printer paper and ink"),
        Expense(date=today, category="miscellaneous", amount=300, description="Staff incentives"),
    ]
    db.add_all(expense_data)
    db.commit()

    ira = IRAAllocation(
        month=today.month,
        year=today.year,
        total_ira=50000,
        infrastructure_percent=40,
        health_percent=20,
        education_percent=12,
        other_percent=28,
    )
    db.add(ira)
    db.commit()

    balance = 0
    for revenue in revenue_data:
        balance += revenue.amount
        ledger = TransactionLedger(
            transaction_type="revenue",
            transaction_id=revenue.id,
            date=revenue.date,
            description=f"Revenue: {revenue.source_type}",
            credit_amount=revenue.amount,
            running_balance=balance,
        )
        db.add(ledger)

    for expense in expense_data:
        balance -= expense.amount
        ledger = TransactionLedger(
            transaction_type="expense",
            transaction_id=expense.id,
            date=expense.date,
            description=f"Expense: {expense.category}",
            debit_amount=expense.amount,
            running_balance=balance,
        )
        db.add(ledger)

    db.commit()
    print("Database seeded successfully!")
    db.close()

if __name__ == "__main__":
    seed_database()

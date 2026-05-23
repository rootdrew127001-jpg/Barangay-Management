from datetime import date, datetime, timedelta
import hashlib
from .database import SessionLocal, engine
from .models import Base, User, Revenue, Expense, IRAAllocation, TransactionLedger

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    if db.query(Revenue).first():
        print("Database already seeded. Skipping seed operation.")
        db.close()
        return

    users = [
        User(username="admin", password_hash=get_password_hash("admin123"), role="admin"),
        User(username="treasurer", password_hash=get_password_hash("treasurer123"), role="treasurer"),
    ]
    db.add_all(users)
    db.commit()
    print("Users created")

    today = date.today()
    
    revenue_data = [
        Revenue(date=today, source_type="community_tax", amount=10000, or_number="OR-001", payment_status="paid"),
    ]
    db.add_all(revenue_data)
    db.commit()

    expense_data = [
        Expense(date=today, category="utilities", amount=2000, description="Operating expenses"),
    ]
    db.add_all(expense_data)
    db.commit()

    print("Revenue and Expense data seeded (₱10,000 revenue, ₱2,000 expenses)")

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
    print("Database seeded successfully! Data is now in your hands - seed_data will never run again.")
    db.close()

if __name__ == "__main__":
    seed_database()

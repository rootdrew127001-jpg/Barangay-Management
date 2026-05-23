from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers import revenue, expenses, reports, transactions, ira
from .seed_data import seed_database

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Barangay Financial Management API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(revenue.router)
app.include_router(expenses.router)
app.include_router(reports.router)
app.include_router(transactions.router)
app.include_router(ira.router)

@app.on_event("startup")
def startup_event():
    seed_database()

@app.get("/health")
def health_check():
    return {"status": "ok"}

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .database import engine
from .models import Base
from .routers import revenue, expenses, reports, transactions, ira, residents
from .seed_data import seed_database

Base.metadata.create_all(bind=engine)

FRONTEND_DIR = Path(__file__).resolve().parent.parent
HOME_PAGE = FRONTEND_DIR / "FinancialHome.html"

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
app.include_router(residents.router)

@app.on_event("startup")
def startup_event():
    seed_database()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/")
def serve_home():
    return FileResponse(HOME_PAGE)

@app.get("/financialhome.html")
def serve_home_lowercase():
    return FileResponse(HOME_PAGE)

app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")

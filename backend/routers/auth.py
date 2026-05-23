from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import hashlib
from datetime import datetime, timedelta
from jose import JWTError, jwt
from ..models import User
from ..schemas import LoginRequest, TokenResponse, UserResponse
from ..database import get_db
from ..config import SECRET_KEY

router = APIRouter(prefix="/api/auth", tags=["auth"])

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password

def create_access_token(user_id: int, expires_delta: timedelta = None):
    if expires_delta is None:
        expires_delta = timedelta(hours=24)
    expire = datetime.utcnow() + expires_delta
    to_encode = {"sub": str(user_id), "exp": expire}
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def get_current_user(token: str, db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        user_id: int = int(payload.get("sub"))
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == request.username).first()
    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id)
    return TokenResponse(token=token, user=UserResponse.from_orm(user))

@router.post("/logout")
def logout():
    return {"message": "Logged out successfully"}

@router.get("/me", response_model=UserResponse)
def get_current_user_info(token: str = None, db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Token required")
    user = get_current_user(token, db)
    return user

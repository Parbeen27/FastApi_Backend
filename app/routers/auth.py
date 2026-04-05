from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from schemas import UserCreate,UserOut
import models, auth

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.hash_password(user.password)
    new_user = models.User(email=user.email, password=hashed, role=user.role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    account = models.Account(user_id=new_user.id, balance=0)
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"email": new_user.email, "id": new_user.id}

@router.post("/login")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user :
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not auth.verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = auth.create_access_token(data={"user_id": db_user.id, "role": db_user.role})
    return {"access_token": token, "token_type": "bearer"}

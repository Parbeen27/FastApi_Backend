from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Transaction, Account, User
from auth import get_current_user,get_db
from decimal import Decimal

router = APIRouter()

@router.get("/summary/")
def get_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # 1️⃣ Get the logged-in user's account
    account = db.query(Account).filter(Account.user_id == current_user["user_id"]).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    # 2️⃣ Get transactions where user is sender or receiver
    transactions = db.query(Transaction).filter(
        (Transaction.user_id == account.id) | (Transaction.receiver_id == account.id)
    ).all()

    # 3️⃣ Compute income and expenses
    income = sum(
        t.amount for t in transactions
        if t.type == "deposit" or (t.type == "transfer" and t.receiver_id == account.id)
    )
    expenses = sum(
        t.amount for t in transactions
        if t.type == "withdraw" or (t.type == "transfer" and t.user_id == account.id)
    )

    balance = income - expenses

    summary = {"income": float(income), "expenses": float(expenses), "balance": float(balance)}
    return {"message": "Summary created successfully", "summary": summary}
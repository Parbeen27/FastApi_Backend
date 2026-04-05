from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from auth import get_current_user
from sqlalchemy.orm import Session
from .users import require_role
from schemas import TransactionCreate
from auth import get_db
from models import Account,Transaction,User
from decimal import Decimal

router = APIRouter()

def create_transaction_service(db: Session, user_id: int, data: TransactionCreate):

    # 1. Get sender account
    account = db.query(Account).filter(Account.user_id == user_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")

    amount = Decimal(data.amount)

    # 2. Deposit
    if data.type == "deposit":
        account.balance += amount

    # 3. Withdraw
    elif data.type == "withdraw":
        if account.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient Balance")
        account.balance -= amount

    # 4. Transfer
    elif data.type == "transfer":
        if account.balance < amount:
            raise HTTPException(status_code=400, detail="Insufficient Balance")

        if not data.receiver_email:
            raise HTTPException(status_code=400, detail="Receiver email is required")

        # ✅ Step 1: find user by email
        receiver_user = db.query(User).filter(User.email == data.receiver_email).first()
        if not receiver_user:
            raise HTTPException(status_code=404, detail="Receiver not found")

        # ✅ Step 2: find account using user.id
        receiver_account = db.query(Account).filter(Account.user_id == receiver_user.id).first()
        if not receiver_account:
            raise HTTPException(status_code=404, detail="Receiver account not found")

        if receiver_account.id == account.id:
            raise HTTPException(status_code=400, detail="Cannot transfer to yourself")

        # Transfer money
        account.balance -= amount
        receiver_account.balance += amount

    else:
        raise HTTPException(status_code=400, detail="Invalid transaction type")

    # 5. Save transaction
    transaction = Transaction(
        user_id=account.user_id,  # ✅ FIX: store account.id
        receiver_id=receiver_account.id if data.type == "transfer" else None,
        amount=amount,
        type=data.type,
        created_at=datetime.now(timezone.utc)
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return transaction

@router.post("/transactions/")
def create_transaction(transaction: TransactionCreate,db: Session = Depends(get_db) ,current_user: dict = Depends(require_role(["user"]))):
    return create_transaction_service(db, current_user["user_id"], transaction)

@router.get("/transactions/")
def read_transactions(current_user: dict = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Transaction).filter(Transaction.user_id == current_user["user_id"]).all()

from fastapi import APIRouter, Depends, HTTPException,Query
from sqlalchemy.orm import Session
from auth import get_current_user,get_db
from schemas import UserCreate
import models,schemas as schemas,auth
from datetime import datetime

class Roles:
    ADMIN = "admin"
    ANALYST = "analyst"
    USER = "user"

router = APIRouter()
#finding roles of current user to allows role based access
def require_role(allowed_roles: list):
    def role_checker(user: dict = Depends(get_current_user)):
        if user["role"] not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )
        return user
    return role_checker

#admin role only 
@router.post("/admin/users",status_code=201)
def create_user(
    user_data: UserCreate,db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([Roles.ADMIN]))    
    ):
    existing_user = db.query(models.User).filter(models.User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="user already exists")
    hashed = auth.hash_password(user_data.password)

    new_user = models.User(
        email=user_data.email,
        password=hashed,
        role=user_data.role
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    account = models.Account(user_id=new_user.id, balance=0)
    db.add(account)
    db.commit()
    db.refresh(account)
    return {"email": new_user.email, "id": new_user.id}


@router.delete("/admin/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role([Roles.ADMIN]))
):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"msg": f"User {user_id} deleted"}

@router.put("/admin/users/{user_id}/role")
def update_user_role(
    user_id: int,
    role: str,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin"]))
):
    user = db.query(models.User).filter(models.User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.role = role
    db.commit()

    return {"msg": f"User role updated to {role}"}


#analyst role only 
@router.get("/analytics/transactions")
def get_transactions(
    min_amount: float = None,
    max_amount: float = None,
    start_date: datetime = None,
    end_date: datetime = None,
    sort_by:str = "date",
    order: str = "desc",
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_role(["admin", "analyst"]))
):
    query = db.query(models.Transaction)

    if min_amount is not None:
        query = query.filter(models.Transaction.amount >= min_amount)

    if max_amount is not None:
        query = query.filter(models.Transaction.amount <= max_amount)

    # ✅ NEW: date filters
    if start_date:
        query = query.filter(models.Transaction.created_at >= start_date)

    if end_date:
        query = query.filter(models.Transaction.created_at <= end_date)
    
    if sort_by == "amount":
        column = models.Transaction.amount
    else:
        column = models.Transaction.created_at

    if order == "asc":
        query = query.order_by(column.asc())
    else:
        query = query.order_by(column.desc())

    return query.all()


#all three roles can access
@router.get("/users")
def read_user_data(
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user),
    user_id: int = Query(None, description="User ID (admins/analysts only)")
):

    # Role check
    if current_user["role"] in ["admin", "analyst"]:
        # Admin or analyst: can view requested user or all users if user_id is None
        if user_id:
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
        else:
            # No user_id provided: return all users
            users = db.query(models.User).all()
            return users
    else:
        # Regular user: ignore user_id, always return own data
        user = db.query(models.User).filter(models.User.id == current_user["user_id"]).first()

    return user
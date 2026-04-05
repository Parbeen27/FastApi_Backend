from sqlalchemy import Column, Integer, String, Float, ForeignKey,Numeric,DateTime
from database import Base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

# Define User and Transaction models
class User(Base):
    __tablename__ = "users" # Table name in the database
    id = Column(Integer, primary_key=True) 
    email = Column(String, unique=True, index=True) # User's email, must be unique and indexed for faster queries
    password = Column(String)  # Hashed password for security

    # Role can be 'user' or 'admin and analyst', default is 'user'
    role = Column(String,default="user")  

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    balance = Column(Numeric(12,2), default=0) 

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True) # Primary key for the transaction
    amount = Column(Numeric(12,2),nullable=False) # Amount of the transaction
    type = Column(String, nullable=False) # Type of transaction, e.g., 'income' or 'expense'
    category = Column(String) # Category of the transaction, e.g., 'food', 'rent', etc.
    user_id = Column(Integer, ForeignKey("accounts.id"), nullable=False) # Foreign key linking to the user who made the transaction
    receiver_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    created_at = Column(DateTime, index=True,default=lambda: datetime.now(timezone.utc))

    sender = relationship("Account", foreign_keys=[user_id])
    receiver = relationship("Account", foreign_keys=[receiver_id])
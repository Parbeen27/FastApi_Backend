from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Annotated
from decimal import Decimal

# Schemas for user creation and transaction creation
class UserCreate(BaseModel):
    username: str
    email: str
    # Password must be between 6 and 72 characters for security reasons
    password: str = Field(...,  max_length=72)
    role: str = "user"

class UserOut(BaseModel):
    id: int
    email: str
    #username: str

    
        
class login(BaseModel):
    email: str
    password: str

class TransactionCreate(BaseModel):
    type: str
    amount: Annotated[Decimal, Field(gt=0, max_digits=12, decimal_places=2)]
    receiver_email: Optional[EmailStr] = None
    description: Optional[str] = None

TransactionCreate.model_rebuild()




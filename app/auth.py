import bcrypt
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from database import SessionLocal
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES




security = HTTPBearer() # Create an instance of HTTPBearer for handling authentication in FastAPI routes


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
# Password hashing Function
def hash_password(password: str):
    password = password.encode('utf-8')[:72] # bcrypt has a maximum password length of 72 bytes, so we encode and truncate the password to ensure it fits within this limit
    hashed = bcrypt.hashpw(password, bcrypt.gensalt()) # Hash the password using bcrypt and return the hashed version
    return hashed.decode('utf-8') # Decode the hashed password back to a string for storage in the database

# verify password
def verify_password(plain_password, hashed_password):
    plain_password = plain_password.encode('utf-8')[:72] # Encode and truncate the plain password to ensure it fits within bcrypt's limit
    hashed_password = hashed_password.encode('utf-8') # Encode the stored hashed password to
    return bcrypt.checkpw(plain_password, hashed_password)

# Function to create a JWT access token with user data
def create_access_token(data: dict):
    to_encode = data.copy() # Create a copy of the input data to avoid modifying 
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES) # Set the expiration time for the token
    to_encode.update({"exp": expire}) # Add the expiration time to the token data
    encode_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM) # Encode the token data into a JWT using the secret key and specified algorithm
    return encode_jwt

# Function to get the current user from the JWT token
def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM]) # Decode the JWT token to extract the payload
        print("payload", payload)
        user_id: int = payload.get("user_id") # Extract the user ID from the payload
        role: str = payload.get("role") # Extract the user role from the payload
        if user_id is None or role is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") # Raise an exception if the token is invalid
        return {"user_id": user_id, "role": role} # Return the user ID and role as a dictionary
    except jwt.JWTError as e:
        print("Jwt Error:", str(e))
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") # Raise an exception if there is an error decoding the token
    

        
        
from fastapi import FastAPI
from database import engine, Base
from routers import auth, transactions, summary, users


# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(users.router,prefix="/auth", tags=["roles"])
app.include_router(transactions.router, prefix="/api", tags=["User_transactions"])
app.include_router(summary.router, prefix="/api", tags=["User_summary"])

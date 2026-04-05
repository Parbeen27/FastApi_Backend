from sqlalchemy import create_engine
from sqlalchemy.orm  import declarative_base, sessionmaker

from config import DATABASE_URL


# SQLAlchemy setup
engine = create_engine(DATABASE_URL, 
                       connect_args={"check_same_thread": False}) # Only needed for SQLite

# Create a configured "Session" class
SessionLocal = sessionmaker(bind=engine) 

# Create a Base class for our models to inherit from
Base = declarative_base()
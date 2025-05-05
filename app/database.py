from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from decouple import config

# Load database credentials from .env
DATABASE_URL = f"mysql+pymysql://{config('MYSQL_USERNAME')}:{config('MYSQL_PASSWORD')}@{config('MYSQL_HOST')}:{config('MYSQL_PORT')}/{config('MYSQL_DATABASE')}"

# Create the database engine
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create all tables
Base.metadata.create_all(bind=engine)

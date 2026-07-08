from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os

# Add the project root to sys.path to import app modules
sys.path.append(os.getcwd())

from app.database import engine
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

Session = sessionmaker(bind=engine)
session = Session()

user = session.query(User).filter(User.email == "admin@example.com").first()
if user:
    user.hashed_password = hash_password("admin123")
    session.commit()
    print("Password for admin@example.com reset to 'admin123'")
else:
    print("User admin@example.com not found")

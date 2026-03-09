# user_api.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, constr
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
import bcrypt
import jwt
import os
from typing import List

# Veritabanı ayarları
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/dbname")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# JWT ayarları
SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Kullanıcı Modeli
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)

# Pydantic Şemaları
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: constr(min_length=6)

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        orm_mode = True

# FastAPI Uygulaması
app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Veritabanı Bağlantısı
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Kullanıcı oluşturma
@app.post("/users/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Kullanıcıyı veritabanında kontrol et
    existing_user = db.query(User).filter(User.username == user.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # Şifreyi hash'le
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(username=user.username, email=user.email, hashed_password=hashed_password.decode('utf-8'))

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

# Kullanıcıyı ID ile okuma
@app.get("/users/{user_id}", response_model=UserResponse)
def read_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Kullanıcı güncelleme
@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db_user.username = user.username
    db_user.email = user.email
    db_user.hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    db.commit()
    db.refresh(db_user)
    return db_user

# Kullanıcı silme
@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(db_user)
    db.commit()
    return {"detail": "User deleted"}

# Kullanıcı oturumu açma ve token alma
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not bcrypt.checkpw(form_data.password.encode('utf-8'), user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})

    # JWT Token oluştur
    token_data = {"sub": user.username}
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}

# API dokümantasyonu
@app.get("/")
def read_root():
    return {"Hello": "World"}
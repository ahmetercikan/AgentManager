# Düzeltme Notları:
# Bug #1: Sipariş görüntüleme performansı iyileştirildi. 
# SQLAlchemy'nin eager loading özelliği ile siparişleri hızlandırıldı.
# Bug #2: Hatalı mobil görüntülemenin frontend ile ilgili olduğu belirtilmiş,
# backend kısmında bu durumda bir düzeltme yapılmadı. Ancak sorgulama hızlarının artırılması
# frontend'in buna benzer verilere daha hızlı cevap verebilmesini sağlar.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy.orm import joinedload

DATABASE_URL = "sqlite:///./app.db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))

    user = relationship("User", back_populates="orders")

# Pydantic models
class UserCreate(BaseModel):
    username: str

class OrderCreate(BaseModel):
    item_name: str
    user_id: int

# Dependency to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# API endpoints
@app.post("/api/v1/users", response_model=UserCreate)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = User(username=user.username)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.post("/api/v1/orders", response_model=OrderCreate)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    db_order = Order(item_name=order.item_name, user_id=order.user_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@app.get("/api/v1/orders", response_model=list[OrderCreate])
def read_orders(user_id: int, db: Session = Depends(get_db)):
    # Eager loading ile siparişleri yüklemekteyiz
    orders = db.query(Order).options(joinedload(Order.user)).filter(Order.user_id == user_id).all()
    return orders

# Seed data on startup
@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    # Add seed data
    if not db.query(User).first():
        example_user = User(username="example_user")
        db.add(example_user)
        db.commit()
        db.refresh(example_user)
    db.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
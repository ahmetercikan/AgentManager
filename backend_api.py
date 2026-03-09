from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, Integer, String, Text, Numeric, ForeignKey, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
import bcrypt

DATABASE_URL = "sqlite:///./test.db"  # SQLite, but can be any DB
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Veritabanı Modelleri
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(EmailStr, unique=True, index=True)
    password = Column(String)
    created_at = Column(Date, default=datetime.utcnow)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text)
    price = Column(Numeric)
    stock = Column(Integer)
    category_id = Column(Integer, ForeignKey("categories.id"))
    created_at = Column(Date, default=datetime.utcnow)

class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)

class Order(Base):
    __tablename__ = "orders"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_amount = Column(Numeric)
    status = Column(String)
    created_at = Column(Date, default=datetime.utcnow)

class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)

# Pydantic Modelleri
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    stock: int
    category_id: int

class OrderCreate(BaseModel):
    user_id: int
    total_amount: float
    status: str

class CartCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int

# CRUD İşlemleri
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/auth/register")
def register(user: UserCreate, db: SessionLocal = Depends(get_db)):
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    db_user = User(name=user.name, email=user.email, password=hashed_password.decode('utf-8'))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return {"message": "User created successfully"}

@app.post("/api/auth/login")
def login(email: EmailStr, password: str, db: SessionLocal = Depends(get_db)):
    user = db.query(User).filter(User.email == email).first()
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user.password.encode('utf-8')):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    return {"message": "Login successful"}

@app.post("/api/products")
def create_product(product: ProductCreate, db: SessionLocal = Depends(get_db)):
    db_product = Product(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

@app.get("/api/products")
def read_products(skip: int = 0, limit: int = 10, db: SessionLocal = Depends(get_db)):
    products = db.query(Product).offset(skip).limit(limit).all()
    return products

@app.get("/api/products/{product_id}")
def read_product(product_id: int, db: SessionLocal = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@app.put("/api/products/{product_id}")
def update_product(product_id: int, product: ProductCreate, db: SessionLocal = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    for key, value in product.dict().items():
        setattr(db_product, key, value)
    db.commit()
    return db_product

@app.delete("/api/products/{product_id}")
def delete_product(product_id: int, db: SessionLocal = Depends(get_db)):
    db_product = db.query(Product).filter(Product.id == product_id).first()
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    db.delete(db_product)
    db.commit()
    return {"message": "Product deleted"}

@app.post("/api/orders")
def create_order(order: OrderCreate, db: SessionLocal = Depends(get_db)):
    db_order = Order(**order.dict())
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

@app.post("/api/cart")
def add_to_cart(cart: CartCreate, db: SessionLocal = Depends(get_db)):
    db_cart = Cart(**cart.dict())
    db.add(db_cart)
    db.commit()
    db.refresh(db_cart)
    return db_cart

@app.delete("/api/cart/{cart_id}")
def remove_from_cart(cart_id: int, db: SessionLocal = Depends(get_db)):
    db_cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if db_cart is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    db.delete(db_cart)
    db.commit()
    return {"message": "Cart item removed"}

# Veritabanı oluşturma
Base.metadata.create_all(bind=engine)
# Bug Fix: Ensure that the description field is not null when seeding data and handle the retrieval of books properly.

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Sequence
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session

# Database configuration
DATABASE_URL = "sqlite:///./app.db"
Base = declarative_base()

# Create a FastAPI instance
app = FastAPI()

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# SQLAlchemy model for the Book
class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, Sequence('book_id_seq'), primary_key=True)
    title = Column(String(255), nullable=False)
    author = Column(String(255), nullable=False)
    description = Column(String, nullable=False)  # Changed to nullable=False

# Create the database engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create all tables in the database
Base.metadata.create_all(bind=engine)

# Create a new session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Seed data
@app.on_event("startup")
def startup_event():
    db: Session = SessionLocal()
    # Add seed data if the table is empty
    if db.query(Book).count() == 0:
        books = [
            Book(title="Book One", author="Author A", description="This is a book about the first topic."),
            Book(title="Book Two", author="Author B", description="This is a book about the second topic."),
            Book(title="Book Three", author="Author C", description="This is a book about the third topic."),
        ]
        db.bulk_save_objects(books)
        db.commit()
    db.close()

# Endpoint to get all books
@app.get("/api/v1/books")
def get_books():
    db: Session = SessionLocal()
    books = db.query(Book).all()
    db.close()
    return {"data": books}

# Error handling for not found
@app.get("/api/v1/books/{book_id}")
def get_book(book_id: int):
    db: Session = SessionLocal()
    book = db.query(Book).filter(Book.id == book_id).first()
    db.close()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book

# Main function to start the server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
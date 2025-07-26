from fastapi import FastAPI, HTTPException, status, Query
from pydantic import BaseModel, Field
from typing import List

app = FastAPI()

# class Book(BaseModel):
#     title: str
#     author: str
#     description: str
#     rating: int
class Book(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="The title of the book (1-100 characters)")
    author: str = Field(..., min_length=1, max_length=100, description="The author of the book (1-100 characters)")
    description: str = Field(..., min_length=1, max_length=500, description="A brief description of the book (1-500 characters)")
    rating: int = Field(..., ge=1, le=5, description="Rating of the book (1-5)")
    published_year: int = Field(..., ge=1900, le=2025, description="The year the book was published (1900-2025)")


books = []

@app.post("/books/", response_model=Book)
async def create_book(book : Book):
    books.append(book)
    return book

@app.get("/books/", response_model=List[Book])
async def get_books():
    return books

@app.get("/books/{book_title}", response_model=Book)
async def get_book(book_title:str):
    for book in books:
        if book.title == book_title:
            return book
        raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")
    
@app.put("/books/{book_title}", response_model=Book)
async def update_book(book_title: str, book:Book):
    for index, existing_book in enumerate(books):
        if existing_book.title == book_title:
            books[index] = book
            return book
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Book not found")
    

@app.delete("/books/{book_title}", response_model=dict)
async def delete_book(book_title: str):
    for index, book in enumerate(books):
        if book.title == book_title:
            del books[index]
            return {"message": "Book deleted successfully"}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

@app.get("/")
async def read_books(limit: int = Query(10, ge=1, le=100), published_after: int = Query(2000, ge=1900, le=2025)):
    filtered_books = [book for book in books if books.published_year >= published_after]
    return filtered_books[:limit]
# from fastapi import FastAPI, HTTPException, status, Query, Depends, Request
# from pydantic import BaseModel, Field
# from typing import List
# import time
# import asyncio


# app = FastAPI()

# # class Book(BaseModel):
# #     title: str
# #     author: str
# #     description: str
# #     rating: int
# class Book(BaseModel):
#     title: str = Field(..., min_length=1, max_length=100, description="The title of the book (1-100 characters)")
#     author: str = Field(..., min_length=1, max_length=100, description="The author of the book (1-100 characters)")
#     description: str = Field(..., min_length=1, max_length=500, description="A brief description of the book (1-500 characters)")
#     rating: int = Field(..., ge=1, le=5, description="Rating of the book (1-5)")
#     published_year: int = Field(..., ge=1900, le=2025, description="The year the book was published (1900-2025)")


# books = []

# @app.post("/books/", response_model=Book, tags=["Books"])
# async def create_book(book : Book):
#     books.append(book)
#     return book

# @app.get("/books/", response_model=List[Book], tags=["Books"])
# async def get_books():
#     return books

# @app.get("/books/{book_title}", response_model=Book, tags=["Books"])
# async def get_book(book_title:str):
#     for book in books:
#         if book.title == book_title:
#             return book
#         raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Book not found")
    
# @app.put("/books/{book_title}", response_model=Book, tags=["Books"])
# async def update_book(book_title: str, book:Book):
#     for index, existing_book in enumerate(books):
#         if existing_book.title == book_title:
#             books[index] = book
#             return book
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Book not found")
    

# @app.delete("/books/{book_title}", response_model=dict, tags=["Books"])
# async def delete_book(book_title: str):
#     for index, book in enumerate(books):
#         if book.title == book_title:
#             del books[index]
#             return {"message": "Book deleted successfully"}
#     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Book not found")

# @app.get("/", tags=["Root"])
# async def read_books(limit: int = Query(10, ge=1, le=100), published_after: int = Query(2000, ge=1900, le=2025)):
#     filtered_books = [book for book in books if books.published_year >= published_after]
#     return filtered_books[:limit]

# # Sync and Async Tasks

# @app.get("/sync-task/", tags=["Sync"])
# def sync_task():
#     time.sleep(5)
#     return {"message": "sync task completed"}

# @app.get("/async-task/", tags=["Async"])
# async def async_task():
#     await asyncio.sleep(5)  # Non-blocking, async task
#     return {"message": "Async task completed"}


# async def log_request(request: Request):
#     print(f"Request path: {request.url.path}")
#     return {"path": request.url.path}


# @app.get("/log/", dependencies=[Depends(log_request)], tags=["Logging"])
# async def log_route():
#     return {"message": "Logging request path"}


# # Simulaed Database Dependency 
# class FackeDBSession:
#     def __init__(self):
#         self.connection = "Fake DB Connection"
    
#     def close(self):
#         print("Closing fake DB connection")

# async def get_db():
#     db = FackeDBSession()
#     try:
#         yield db
#     finally:
#         db.close()

# @app.get("/items/", tags = ["FakeDB"])
# async def read_items(db: FackeDBSession = Depends(get_db)):
#     return {"db_connection": db.connection, "message": "Items fetched successfully"}


import jwt
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, status, Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

app = FastAPI()

# Secret and algorithm
SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Fake user DB
fake_users_db = {
    "johndoe": {"username": "johndoe", "password": "secretpassword"}
}

# Model for login
class Login(BaseModel):
    username: str
    password: str

# Create JWT token
def create_jwt_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify JWT token
def verify_jwt_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

# JWT Bearer dependency
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = verify_jwt_token(token)
    return payload

# Login route
@app.post("/login", tags=["Authentication"])
async def login(user: Login):
    db_user = fake_users_db.get(user.username)
    if not db_user or db_user["password"] != user.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    
    token_data = {"sub": user.username}
    token = create_jwt_token(token_data)
    return {"access_token": token, "token_type": "bearer"}

# Protected route
@app.get("/protected", tags=["Protected"])
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello, {current_user['sub']}! You are authenticated."}

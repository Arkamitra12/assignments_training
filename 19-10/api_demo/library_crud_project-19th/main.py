from fastapi import FastAPI, HTTPException
 
from pydantic import BaseModel
 
import psycopg2
 
app = FastAPI()
 
 
class Book(BaseModel):
    book_id: int
    title: str
    author: str
    category: str
    price: float
    stock: int
 
books=[]
 
def get_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="library_store",
        user="postgres",
        password="Admin@123")
    print("Connected to PostgreSQL")
 
    return conn
#
@app.get("/books")
def get_books():
    conn = get_connection()
 
    cursor = conn.cursor()
 
    cursor.execute("SELECT * FROM books")
 
    rows = cursor.fetchall()
 
    cursor.close()
 
    conn.close()
 
    return rows
# @app.get("/books")
# def get_books():
#     conn = get_connection()
#
#     cursor = conn.cursor()
#
#     cursor.execute("SELECT * FROM books where category = 'Technology'",)
#
#     rows = cursor.fetchall()
#
#     cursor.close()
#
#     conn.close()
#
#     return rows
 
 
@app.post("/books")
def add_book(books:Book):
    conn = get_connection()
 
    cursor = conn.cursor()
 
    cursor.execute("""INSERT INTO books(book_id,title,author,category,price,stock)
     VALUES(%s,%s,%s,%s,%s,%s)""",
                   (books.book_id,books.title,books.author,books.category,books.price,books.stock) )
 
    conn.commit()
 
    cursor.close()
 
    conn.close()
 
    return {
 
        "message": "Book added successfully",
        "product": books
 
    }
 
 
@app.put("/books/{book_id}")
def update_books(book_id: int, books: Book):
    conn = get_connection()
 
    cursor = conn.cursor()
 
    cursor.execute("""
    UPDATE books
    SET title = %s, author = %s, category = %s, price = %s, stock = %s
    WHERE id = %s)"""),
 
    if cursor.rowcount == 0:
        cursor.close()
 
        conn.close()
 
        raise HTTPException(
 
            status_code=404,
 
            detail="Book not found"
 
        )
 
    conn.commit()
 
    cursor.close()
 
    conn.close()
 
    return {
 
        "message": "Book updated successfully"
 
    }
#
#
# @app.delete("/books/{book_id}")
# def delete_books(book_id: int):
#     conn = get_connection()
#
#     cursor = conn.cursor()
#
#     cursor.execute(
#
#         "DELETE FROM books WHERE id = %s",
#
#         (book_id,)
#
#     )
#
#     if cursor.rowcount == 0:
#         cursor.close()
#
#         conn.close()
#
#         raise HTTPException(
#
#             status_code=404,
#
#             detail="Book not found"
#
#         )
#
#     conn.commit()
#
#     cursor.close()
#
#     conn.close()
#
#     return {
#
#         "message": "Book deleted successfully"
#
#     }
#
 
 
conn = get_connection()
conn.close()
has context menu

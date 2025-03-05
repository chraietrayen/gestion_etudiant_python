from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3

app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for student data
class Student(BaseModel):
    name: str
    age: int
    grade: str

# SQLite DB connection
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row  # Fetch rows as dictionaries
    return conn

# Create students table if not exists
def create_table():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            grade TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

create_table()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Student API!"}

# POST request to add student
@app.post("/students/")
def add_student(student: Student):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO students (name, age, grade) VALUES (?, ?, ?)", 
            (student.name, student.age, student.grade)
        )
        conn.commit()
        conn.close()
        return {"message": "Student added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# GET request to fetch all students
@app.get("/students/", response_model=List[Student])
def get_students():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        conn.close()
        return [
            {"id": row["id"], "name": row["name"], "age": row["age"], "grade": row["grade"]}
            for row in students
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DELETE request to remove student by ID
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()

        # Check if student exists
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")

        conn.close()
        return {"message": "Student deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

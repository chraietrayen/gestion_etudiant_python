from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import sqlite3

# Création de l'instance FastAPI
app = FastAPI()

# Configuration CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèle Pydantic pour Student
class Student(BaseModel):
    name: str
    age: int
    grade: str

# Modèle pour inclure l'ID dans la réponse
class StudentResponse(Student):
    id: int

# Fonction pour obtenir la connexion à la base de données
def get_db():
    conn = sqlite3.connect("students.db")
    conn.row_factory = sqlite3.Row  # Permet de récupérer les résultats sous forme de dictionnaire
    return conn

# Création de la table si elle n'existe pas
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

# Appel de la fonction pour s'assurer que la table existe
create_table()

# Endpoint racine
@app.get("/")
def read_root():
    return {"message": "Welcome to the Student API!"}

# Ajouter un étudiant
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
        student_id = cursor.lastrowid  # Récupérer l'ID généré
        conn.close()
        return {"message": "Student added successfully", "id": student_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Récupérer tous les étudiants
@app.get("/students/", response_model=List[StudentResponse])
def get_students():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        conn.close()
        return [{"id": row["id"], "name": row["name"], "age": row["age"], "grade": row["grade"]} for row in students]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Supprimer un étudiant par ID
@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Student not found")

        conn.close()
        return {"message": "Student deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

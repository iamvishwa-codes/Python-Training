from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
from passlib.context import CryptContext

app = FastAPI()

# --------------------------
# Password hashing
# --------------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --------------------------
# Database configuration
# --------------------------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "vishwa@12345"
DB_NAME = "banking"

# --------------------------
# Initialize DB
# --------------------------
def init_db():
    try:
        # Connect without specifying a database
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        conn.close()

        # Connect to the new database and create table
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                balance FLOAT DEFAULT 0
            )
        """)
        conn.commit()
        cursor.close()
        conn.close()
        print("Database and table are ready!")
    except Error as e:
        print("Error initializing DB:", e)
        raise

# Initialize DB at startup
init_db()

# --------------------------
# MySQL connection
# --------------------------
def get_db():
    try:
        return mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
    except Error as e:
        raise HTTPException(status_code=500, detail=f"MySQL Connection error: {e}")

# --------------------------
# Models
# --------------------------
class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class Transaction(BaseModel):
    amount: float

# --------------------------
# REGISTER USER
# --------------------------
@app.post("/register")
def register(user: UserCreate):
    hashed_pwd = pwd_context.hash(user.password)
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (user.username, hashed_pwd)
        )
        conn.commit()
    except mysql.connector.errors.IntegrityError:
        raise HTTPException(status_code=400, detail="Username already exists")
    finally:
        cursor.close()
        conn.close()
    return {"message": "User registered successfully"}

# --------------------------
# LOGIN USER
# --------------------------
@app.post("/login")
def login(user: UserLogin):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username=%s", (user.username,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row and pwd_context.verify(user.password, row[0]):
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")

# --------------------------
# GET BALANCE
# --------------------------
@app.get("/balance/{username}")
def get_balance(username: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE username=%s", (username,))
    row = cursor.fetchone()
    cursor.close()
    conn.close()
    if row:
        return {"balance": float(row[0])}
    else:
        raise HTTPException(status_code=404, detail="User not found")

# --------------------------
# DEPOSIT
# --------------------------
@app.post("/deposit/{username}")
def deposit(username: str, txn: Transaction):
    if txn.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + %s WHERE username=%s", (txn.amount, username))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"Deposited {txn.amount} successfully"}

# --------------------------
# WITHDRAW
# --------------------------
@app.post("/withdraw/{username}")
def withdraw(username: str, txn: Transaction):
    if txn.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE username=%s", (username,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    if row[0] < txn.amount:
        cursor.close()
        conn.close()
        raise HTTPException(status_code=400, detail="Insufficient funds")
    cursor.execute("UPDATE users SET balance = balance - %s WHERE username=%s", (txn.amount, username))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": f"Withdrew {txn.amount} successfully"}

# --------------------------
# DELETE ACCOUNT
# --------------------------
@app.delete("/delete/{username}")
def delete_account(username: str):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username=%s", (username,))
    conn.commit()
    cursor.close()
    conn.close()
    return {"message": "Account deleted successfully"}

# main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
import mysql.connector
from mysql.connector import Error
import pandas as pd
from datetime import date, datetime, timedelta
import jwt
import smtplib
from email.mime.text import MIMEText
from passlib.context import CryptContext
from typing import Optional, List, Dict

app = FastAPI(title="Attendance API with JWT + Users")

# -------------------- MYSQL CONFIG --------------------
db_host = "localhost"
db_port = 3306
db_user = "root"
db_password = "vishwa@12345"
db_name = "attendance_db"

# -------------------- JWT CONFIG --------------------
SECRET_KEY = "MY_SECRET_1234"        # CHANGE for production
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60     # 1 hour

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# -------------------- PASSWORD HASHER --------------------
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

# -------------------- EMAIL CONFIG (GMAIL) --------------------
EMAIL_USER = ""            # CHANGE
EMAIL_PASSWORD = ""      # CHANGE (Google App Password)

def send_email(to_email: str, student_name: str):
    msg = MIMEText(f"""
Hello,

Student: {student_name}
Status:absent
Date: {date.today()}

Regards,
Admin
""")
    msg["Subject"] = "Attendance Alert - Student Absent"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.sendmail(EMAIL_USER, [to_email], msg.as_string())
        server.quit()
        print("Email sent to:", to_email)
    except Exception as e:
        print("Email error:", e)

# -------------------- MODELS --------------------
class AttendanceIn(BaseModel):
    student_name: str
    batch: str
    status: str                 # "Present" / "Absent"
    email: str

class RegisterIn(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str

# -------------------- DB HELPERS --------------------
def get_connection(db: Optional[str] = None):
    try:
        return mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db
        )
    except Error as e:
        print("DB connection error:", e)
        return None

@app.on_event("startup")
def startup():
    # create database if not exists
    conn = get_connection()
    if conn is None:
        raise RuntimeError("Cannot connect to MySQL server. Fix DB config.")
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
    conn.commit()
    cur.close()
    conn.close()

    # create tables
    conn = get_connection(db_name)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE,
            password VARCHAR(255)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS attendance(
            id INT AUTO_INCREMENT PRIMARY KEY,
            student_name VARCHAR(255),
            batch VARCHAR(50),
            status VARCHAR(20),
            email VARCHAR(255),
            date DATE
        )
    """)
    conn.commit()

    # ensure default admin exists (hashed password)
    cur.execute("SELECT id FROM users WHERE username = %s", ("admin",))
    if cur.fetchone() is None:
        hashed = hash_password("admin123")
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", ("admin", hashed))
        conn.commit()
        print("Created default admin (username: admin, password: admin123) — password stored hashed.")
    cur.close()
    conn.close()
    print("Startup complete: DB and tables ready.")

# -------------------- JWT HELPERS --------------------
def create_access_token(username: str, pwd_hash: str, expires_minutes: int = ACCESS_TOKEN_EXPIRE_MINUTES) -> str:
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload = {
        "sub": username,
        "pwd_hash": pwd_hash,      # bcrypt hash included per your request (Option 2 → C)
        "exp": expire
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def decode_token(token: str) -> Dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

# -------------------- AUTH DEPENDENCY --------------------
def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict:
    payload = decode_token(token)
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    # verify user still exists and pwd_hash matches DB (added safety)
    conn = get_connection(db_name)
    if conn is None:
        raise HTTPException(status_code=500, detail="DB connection failed")
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="User not found")
    # optional: ensure token's pwd_hash matches DB hash to avoid token reuse after password change:
    token_pwd_hash = payload.get("pwd_hash")
    if token_pwd_hash is None or token_pwd_hash != row[0]:
        raise HTTPException(status_code=401, detail="Invalid token (password changed?)")
    return {"username": username, "pwd_hash": token_pwd_hash}

# -------------------- ROUTES --------------------
@app.get("/", tags=["root"])
def root():
    # 1) When user opens base link -> show successful
    return {"message": "Successful"}

# ----- Register (public) -----
@app.post("/register", status_code=201, tags=["auth"])
def register(data: RegisterIn):
    conn = get_connection(db_name)
    if conn is None:
        raise HTTPException(500, "DB connection failed")
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=%s", (data.username,))
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(400, "Username already exists")
    hashed = hash_password(data.password)
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (data.username, hashed))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": "User registered"}

# ----- Login (form) -----
@app.post("/login", tags=["auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password

    conn = get_connection(db_name)
    if conn is None:
        raise HTTPException(500, "DB connection failed")
    cur = conn.cursor()
    cur.execute("SELECT password FROM users WHERE username=%s", (username,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    stored_hash = row[0]
    if not verify_password(password, stored_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create token that includes username and hashed password (pwd_hash) per request
    token = create_access_token(username=username, pwd_hash=stored_hash)
    # Return token in OAuth2 style so Swagger 'Authorize' uses it in "Value"
    return {"access_token": token, "token_type": "bearer"}

# ----- Authorize Info (so you can see username & password-hash after authorize) -----
@app.get("/authorize-info", tags=["auth"])
def authorize_info(user: dict = Depends(get_current_user)):
    # returns the username and stored password-hash from token
    # (you will see this after pressing "Authorize" and calling this endpoint)
    return {"username": user["username"], "pwd_hash": user["pwd_hash"]}

# ----- Add extra user (protected) -----
@app.post("/users", tags=["users"], status_code=201)
def add_user(data: RegisterIn, current=Depends(get_current_user)):
    # only authenticated user can add another user
    conn = get_connection(db_name)
    if conn is None:
        raise HTTPException(500, "DB connection failed")
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username=%s", (data.username,))
    if cur.fetchone():
        cur.close()
        conn.close()
        raise HTTPException(400, "Username already exists")
    hashed = hash_password(data.password)
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (data.username, hashed))
    conn.commit()
    cur.close()
    conn.close()
    return {"message": f"User {data.username} created by {current['username']}"}

# ----- List users (protected) -----
@app.get("/users", response_model=List[Dict], tags=["users"])
def list_users(current=Depends(get_current_user)):
    conn = get_connection(db_name)
    if conn is None:
        raise HTTPException(500, "DB connection failed")
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT id, username FROM users")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# ----- Mark attendance (protected) -----
@app.post("/attendance", tags=["attendance"])
def mark_attendance(att: AttendanceIn, current=Depends(get_current_user)):
    conn = get_connection(db_name)
    if conn is None:
        raise HTTPException(500, "DB connection failed")
    cur = conn.cursor()
    today = date.today()
    cur.execute("""
        INSERT INTO attendance (student_name, batch, status, email, date)
        VALUES (%s, %s, %s, %s, %s)
    """, (att.student_name, att.batch, att.status, att.email, today))
    conn.commit()
    cur.close()
    conn.close()

    if att.status.strip().lower() == "absent":
        # send real email (configure EMAIL_USER + EMAIL_PASSWORD)
        send_email(att.email, att.student_name)

    return {"message": "Attendance marked"}

# ----- Get attendance (protected) -----
@app.get("/attendance", tags=["attendance"])
def get_attendance(current=Depends(get_current_user)):
    conn = get_connection(db_name)
    if conn is None:
        raise HTTPException(500, "DB connection failed")
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM attendance ORDER BY date DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

# ----- Export to excel (protected) -----
@app.get("/export/{batch_name}", tags=["attendance"])
def export_batch(batch_name: str, current=Depends(get_current_user)):
    conn = get_connection(db_name)
    if conn is None:
        raise HTTPException(500, "DB connection failed")
    query = "SELECT * FROM attendance WHERE batch = %s"
    df = pd.read_sql(query, conn, params=(batch_name,))
    filename = f"attendance_{batch_name}.xlsx"
    df.to_excel(filename, index=False)
    conn.close()
    return {"message": "Excel exported", "file": filename}

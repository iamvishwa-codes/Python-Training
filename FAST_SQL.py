from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# --------------------------
# MySQL Connection
# --------------------------
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="vishwa@12345",
        database="dummy"
    )

# --------------------------
# Pydantic Model
# --------------------------
class User(BaseModel):
    id: int
    name: str
    email: str

# ---------------------------------------------------
# 1️⃣ CREATE USER (POST)
# ---------------------------------------------------
@app.post("/users")
def create_user(user: User):
    try:
        conn = get_db()
        cursor = conn.cursor()

        query = "INSERT INTO users (id, name, email) VALUES (%s, %s, %s)"
        values = (user.id, user.name, user.email)

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return {"message": "User added successfully", "data": user}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------
# 2️⃣ READ ALL USERS (GET)
# ---------------------------------------------------
@app.get("/users")
def get_all_users():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email FROM users")
    rows = cursor.fetchall()

    cursor.close()
    conn.close()

    users = []
    for row in rows:
        users.append({
            "id": row[0],
            "name": row[1],
            "email": row[2]
        })

    return {"users": users}

# ---------------------------------------------------
# 3️⃣ READ SINGLE USER BY ID (GET)
# ---------------------------------------------------
@app.get("/users/{user_id}")
def get_user(user_id: int):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email FROM users WHERE id=%s", (user_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if row:
        return {
            "id": row[0],
            "name": row[1],
            "email": row[2]
        }
    else:
        raise HTTPException(status_code=404, detail="User not found")

# ---------------------------------------------------
# 4️⃣ UPDATE USER (PUT)
# ---------------------------------------------------
@app.put("/users/{user_id}")
def update_user(user_id: int, user: User):
    try:
        conn = get_db()
        cursor = conn.cursor()

        query = "UPDATE users SET name=%s, email=%s WHERE id=%s"
        values = (user.name, user.email, user_id)

        cursor.execute(query, values)
        conn.commit()

        cursor.close()
        conn.close()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ---------------------------------------------------
# 5️⃣ DELETE USER (DELETE)
# ---------------------------------------------------
@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()

        cursor.close()
        conn.close()

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="User not found")

        return {"message": "User deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

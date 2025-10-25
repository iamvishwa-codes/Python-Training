import mysql.connector

# Database configuration
db_host = "localhost"
db_port = 3306
db_user = "root"
db_password = "vishwa@12345"
db_name = "dummy"

def get_connection():
    """Establish and return a database connection."""
    try:
        connection = mysql.connector.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            database=db_name
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def create_student():
    """Insert a new student record."""
    name = input("Enter name: ").strip()
    age = input("Enter age: ").strip()
    if not name or not age.isdigit():
        print("Invalid input. Name must be non-empty and age must be a number.")
        return

    age = int(age)
    connection = get_connection()
    if not connection:
        return

    cur = connection.cursor()
    cur.execute("INSERT INTO student (name, age) VALUES (%s, %s)", (name, age))
    connection.commit()
    print("✅ Student created successfully.")

    cur.close()
    connection.close()


def read_students():
    """Fetch and display all students."""
    connection = get_connection()
    if not connection:
        return

    cur = connection.cursor()
    cur.execute("SELECT id, name, age FROM student")
    rows = cur.fetchall()

    if rows:
        print("\n--- Student List ---")
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Age: {row[2]}")
    else:
        print("No students found.")

    cur.close()
    connection.close()


def update_student():
    """Update an existing student's data."""
    student_id = input("Enter student ID to update: ").strip()
    if not student_id.isdigit():
        print("Invalid ID.")
        return

    name = input("Enter new name: ").strip()
    age = input("Enter new age: ").strip()
    if not name or not age.isdigit():
        print("Invalid input. Name must be non-empty and age must be a number.")
        return

    connection = get_connection()
    if not connection:
        return

    cur = connection.cursor()
    cur.execute("UPDATE student SET name = %s, age = %s WHERE id = %s", (name, int(age), int(student_id)))
    connection.commit()

    if cur.rowcount > 0:
        print("✅ Student updated successfully.")
    else:
        print("❌ Student not found.")

    cur.close()
    connection.close()


def delete_student():
    """Delete a student by ID."""
    student_id = input("Enter student ID to delete: ").strip()
    if not student_id.isdigit():
        print("Invalid ID.")
        return

    connection = get_connection()
    if not connection:
        return

    cur = connection.cursor()
    cur.execute("DELETE FROM student WHERE id = %s", (int(student_id),))
    connection.commit()

    if cur.rowcount > 0:
        print("🗑 Student deleted successfully.")
    else:
        print("❌ Student not found.")

    cur.close()
    connection.close()


def menu():
    """Main menu for CRUD operations."""
    while True:
        print("\n=== Student Management System ===")
        print("1. Create Student")
        print("2. Read Students")
        print("3. Update Student")
        print("4. Delete Student")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            create_student()
        elif choice == "2":
            read_students()
        elif choice == "3":
            update_student()
        elif choice == "4":
            delete_student()
        elif choice == "5":
            print("👋 Exiting program. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 5.")


if __name__ == "__main__":
    menu()
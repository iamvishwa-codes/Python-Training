import datetime
import random
import mysql.connector as sqltor
import pandas as pd

# =========================
# Database connection/setup
# =========================
con = sqltor.connect(
    host="localhost",
    user="root",
    password="vishwa@12345",
    database="dummy",
    port=3306
)
cur = con.cursor(buffered=True)

def setup_db():
    cur.execute("CREATE DATABASE IF NOT EXISTS dummy")
    cur.execute("USE dummy")
    # Patients table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appt (
            idno CHAR(12) PRIMARY KEY,
            name VARCHAR(100),
            age INT,
            gender CHAR(1),
            phone CHAR(10),
            bg VARCHAR(5)
        )
    """)
    # Appointments table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id CHAR(12) NOT NULL,
            doctor_name VARCHAR(100) NOT NULL,
            department VARCHAR(100) NOT NULL,
            room INT NOT NULL,
            appt_date DATE NOT NULL,
            appt_no INT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_patient
                FOREIGN KEY (patient_id) REFERENCES appt(idno)
                ON DELETE CASCADE
        )
    """)
    con.commit()

setup_db()

# =========================
# Data
# =========================
DOCTORS = [
    ("Dr. Varun", "Cardiologist", 201),
    ("Dr. Hrithik", "Cardiologist", 202),
    ("Dr. Salman", "Psychiatrist", 203),
    ("Dr. Shahrukh", "Psychiatrist", 204),
    ("Dr. Akshay", "Otolaryngologist", 205),
    ("Dr. Amir", "Otolaryngologist", 206),
    ("Dr. Sidharth", "Rheumatologist", 207),
    ("Dr. Abhishek", "Rheumatologist", 208),
    ("Dr. Ajay", "Neurologist", 209),
    ("Dr. Ranveer", "Neurologist", 200),
    ("Dr. Irfan", "MI room", 401),
    ("Dr. John", "MI room", 402),
    ("Dr. Sanjay", "MI room", 403),
    ("Dr. Shahid", "MI room", 404),
]

DOCTOR_PASSWORDS = {
    d[0].lower(): 7001+i for i, d in enumerate(DOCTORS)
}

SERVICES = [
    ("X-Ray", 101), ("MRI", 102), ("CT Scan", 103),
    ("Endoscopy", 104), ("Dialysis", 105), ("Ultrasound", 301),
    ("EEG", 302), ("ENMG", 303), ("ECG", 304),
]

# =========================
# Utilities
# =========================
def valid_blood_group(bg):
    return bg.upper() in {"A+", "B+", "O+", "AB+", "A-", "B-", "O-", "AB-"}

def print_patient(idn):
    cur.execute("SELECT idno, name, age, gender, phone, bg FROM appt WHERE idno=%s", (idn,))
    row = cur.fetchone()
    if not row:
        print("No record found.")
        return
    print("Patient details:")
    print(f" Aadhaar: {row[0]}")
    print(f" Name: {row[1]}")
    print(f" Age: {row[2]}")
    print(f" Gender: {row[3]}")
    print(f" Phone: {row[4]}")
    print(f" Blood: {row[5]}")

def get_patient_by_aadhaar():
    idn = input("Enter Aadhaar: ").strip()
    cur.execute("SELECT idno, name, age, gender, phone, bg FROM appt WHERE idno=%s", (idn,))
    row = cur.fetchone()
    if not row:
        print("No data found for that Aadhaar.")
        return None
    return row

def ensure_unique_appt_no(doctor_name, appt_date):
    for _ in range(100):
        num = random.randint(10, 99)
        cur.execute("SELECT 1 FROM appointments WHERE doctor_name=%s AND appt_date=%s AND appt_no=%s",
                    (doctor_name, appt_date, num))
        if not cur.fetchone():
            return num
    cur.execute("SELECT COALESCE(MAX(appt_no), 9) FROM appointments WHERE doctor_name=%s AND appt_date=%s",
                (doctor_name, appt_date))
    max_no = cur.fetchone()[0]
    return int(max_no) + 1

# =========================
# Patient operations
# =========================
def register_patient():
    while True:
        idn = input("Enter Aadhaar (12 digits): ").strip()
        if len(idn) == 12 and idn.isdigit():
            cur.execute("SELECT 1 FROM appt WHERE idno=%s", (idn,))
            if cur.fetchone():
                print("A patient with this Aadhaar already exists.")
                return
            break
        print("Invalid Aadhaar. Must be 12 digits.")

    name = input("Patient name: ").strip()
    
    while True:
        try:
            age = int(input("Age: ").strip())
            break
        except ValueError:
            print("Please enter numeric age.")
    
    while True:
        gender = input("Gender (M/F): ").strip().upper()
        if gender in ("M", "F"):
            break
        print("Enter M or F.")
    
    while True:
        phone = input("Phone (10 digits): ").strip()
        if len(phone) == 10 and phone.isdigit():
            break
        print("Invalid phone.")
    
    while True:
        bg = input("Blood group (A+, B+, O+, AB+, A-, B-, O-, AB-): ").strip().upper()
        if valid_blood_group(bg):
            break
        print("Invalid blood group.")
    
    cur.execute("INSERT INTO appt (idno, name, age, gender, phone, bg) VALUES (%s, %s, %s, %s, %s, %s)",
                (idn, name, age, gender, phone, bg))
    con.commit()
    print("Registration complete.")
    print_patient(idn)

def update_patient_field():
    row = get_patient_by_aadhaar()
    if not row:
        return
    idn = row[0]
    print_patient(idn)
    print("Which field do you want to update?")
    print("1) Name 2) Age 3) Gender 4) Phone 5) Blood group 6) Cancel")
    choice = input("Choice: ").strip()
    
    if choice == "1":
        new = input("New name: ").strip()
        cur.execute("UPDATE appt SET name=%s WHERE idno=%s", (new, idn))
    elif choice == "2":
        while True:
            try:
                new = int(input("New age: ").strip())
                break
            except ValueError:
                print("Enter numeric age.")
        cur.execute("UPDATE appt SET age=%s WHERE idno=%s", (new, idn))
    elif choice == "3":
        while True:
            new = input("New gender (M/F): ").strip().upper()
            if new in ("M", "F"):
                break
            print("Enter M or F.")
        cur.execute("UPDATE appt SET gender=%s WHERE idno=%s", (new, idn))
    elif choice == "4":
        while True:
            new = input("New phone (10 digits): ").strip()
            if len(new) == 10 and new.isdigit():
                break
            print("Invalid phone.")
        cur.execute("UPDATE appt SET phone=%s WHERE idno=%s", (new, idn))
    elif choice == "5":
        while True:
            new = input("New blood group: ").strip().upper()
            if valid_blood_group(new):
                break
            print("Invalid blood group.")
        cur.execute("UPDATE appt SET bg=%s WHERE idno=%s", (new, idn))
    else:
        print("Canceled.")
        return

    con.commit()
    print("Updated details:")
    print_patient(idn)

# =========================
# Lists
# =========================
def list_doctors():
    df = pd.DataFrame(DOCTORS, columns=["Name", "Department", "Room"])
    print(df.to_string(index=False))

def list_services():
    df = pd.DataFrame(SERVICES, columns=["Service", "Room"])
    print(df.to_string(index=False))

# =========================
# Appointments
# =========================
def book_appointment():
    row = get_patient_by_aadhaar()
    if not row:
        return
    patient_id = row[0]
    
    departments = sorted(set(d[1] for d in DOCTORS))
    print("Select department:")
    for i, d in enumerate(departments, start=1):
        print(f"{i}) {d}")
    
    try:
        idx = int(input("Choice number: ").strip())
        if not (1 <= idx <= len(departments)):
            print("Invalid choice.")
            return
    except ValueError:
        print("Invalid input.")
        return

    selected_dept = departments[idx - 1]
    candidates = [d for d in DOCTORS if d[1] == selected_dept]
    chosen = random.choice(candidates)

    days_map = {
        "Cardiologist": 3,
        "Rheumatologist": 5,
        "Psychiatrist": 3,
        "Neurologist": 6,
        "Otolaryngologist": 4,
        "MI room": 1
    }
    days = days_map.get(selected_dept, random.choice([1, 3, 4, 5, 6]))
    appt_date = datetime.date.today() + datetime.timedelta(days=days)
    appt_no = ensure_unique_appt_no(chosen[0], appt_date)

    cur.execute("""
        INSERT INTO appointments (patient_id, doctor_name, department, room, appt_date, appt_no)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (patient_id, chosen[0], chosen[1], chosen[2], appt_date, appt_no))
    con.commit()

    print("Appointment confirmed and saved:")
    print(f" Patient Aadhaar: {patient_id}")
    print(f" Doctor: {chosen[0]} ({chosen[1]})")
    print(f" Room: {chosen[2]}")
    print(f" Date: {appt_date.isoformat()}")
    print(f" Appointment no.: {appt_no}")

# =========================
# Doctor login
# =========================
def doctor_login():
    print("Available doctors:")
    for d, _, _ in DOCTORS:
        print(f" - {d}")
    name_input = input("Enter your doctor name (exact as above, or press Enter to cancel): ").strip()
    if not name_input:
        return
    key = name_input.lower()
    if key not in DOCTOR_PASSWORDS:
        print("Unknown doctor name.")
        return
    try:
        pswd = int(input("Enter password: ").strip())
    except ValueError:
        print("Invalid password format.")
        return
    if pswd != DOCTOR_PASSWORDS[key]:
        print("Wrong password.")
        return

    cur.execute("""
        SELECT a.appt_date, a.appt_no, p.name, p.age, p.idno
        FROM appointments a
        JOIN appt p ON p.idno = a.patient_id
        WHERE a.doctor_name = %s
        ORDER BY a.appt_date ASC, a.appt_no ASC, a.created_at ASC
        LIMIT 100
    """, (name_input,))
    rows = cur.fetchall()
    if not rows:
        print("No appointments found.")
        return
    df = pd.DataFrame(rows, columns=["Date", "Appt No", "Patient Name", "Age", "Aadhaar"])
    print(df.to_string(index=False))

# =========================
# Main menu
# =========================
def main():
    print("Simple Hospital Appointment System")
    print("Date:", datetime.date.today().strftime("%A, %d %B %Y"))
    print("Time:", datetime.datetime.now().strftime("%H:%M:%S"))

    while True:
        print("\nMain menu:")
        print("1) Patient")
        print("2) Doctor")
        print("3) Exit")
        choice = input("Select option: ").strip()
        
        if choice == "1":
            while True:
                print("\nPatient menu:")
                print("1) Register")
                print("2) Book appointment")
                print("3) List doctors")
                print("4) List services")
                print("5) Modify patient data")
                print("6) Back")
                c = input("Choice: ").strip()
                if c == "1":
                    register_patient()
                elif c == "2":
                    book_appointment()
                elif c == "3":
                    list_doctors()
                elif c == "4":
                    list_services()
                elif c == "5":
                    update_patient_field()
                elif c == "6":
                    break
                else:
                    print("Invalid choice.")
        elif choice == "2":
            doctor_login()
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    try:
        main()
    finally:
        con.close()
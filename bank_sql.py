import mysql.connector

# -------------------- MySQL Config --------------------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "vishwa@12345"
DB_NAME = "dummy"
DB_PORT = 3306  # change if needed

# -------------------- Database Connection --------------------
def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            port=DB_PORT
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

# -------------------- Setup Table --------------------
def setup_table():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS accounts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            account_holder VARCHAR(100) UNIQUE NOT NULL,
            pin VARCHAR(10) NOT NULL,
            balance DECIMAL(15,2) DEFAULT 0
        )
        """)
        conn.commit()
        cursor.close()
        conn.close()

# -------------------- BankAccount Class --------------------
class BankAccount:
    def __init__(self, account_holder, pin, balance=0):
        self.account_holder = account_holder
        self.__pin = pin
        self.__balance = balance

    def verify_pin(self, pin):
        return self.__pin == pin

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
            return f"Deposited ₹{amount}. New balance: ₹{self.__balance}"
        else:
            return "Invalid deposit amount."

    def withdraw(self, amount):
        if amount <= 0:
            return "Invalid withdrawal amount."
        elif amount > self.__balance:
            return "Insufficient funds."
        else:
            self.__balance -= amount
            return f"Withdrew ₹{amount}. Remaining balance: ₹{self.__balance}"

    def get_balance(self):
        return self.__balance

# -------------------- CRUD Operations --------------------
def create_account():
    name = input("Enter account holder name: ").strip()
    pin = input("Set 4-digit PIN: ").strip()
    initial_balance = input("Initial deposit (number): ").strip()
    if not name or not pin.isdigit() or len(pin) != 4 or not initial_balance.isdigit():
        print("Invalid input. Try again.")
        return
    initial_balance = float(initial_balance)

    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO accounts (account_holder, pin, balance) VALUES (%s, %s, %s)",
            (name, pin, initial_balance)
        )
        conn.commit()
        print(f"Account created for {name} with balance ₹{initial_balance}")
    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def login():
    name = input("Enter account holder name: ").strip()
    pin = input("Enter 4-digit PIN: ").strip()
    conn = get_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM accounts WHERE account_holder=%s", (name,))
    account_info = cursor.fetchone()
    cursor.close()
    conn.close()

    if not account_info:
        print("Account not found.")
        return None

    account = BankAccount(account_info['account_holder'], account_info['pin'], account_info['balance'])
    if account.verify_pin(pin):
        print(f"Login successful. Welcome {account.account_holder}!")
        return account
    else:
        print("Incorrect PIN.")
        return None

def update_balance(account):
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute("UPDATE accounts SET balance=%s WHERE account_holder=%s",
                   (account.get_balance(), account.account_holder))
    conn.commit()
    cursor.close()
    conn.close()

# -------------------- Main Program --------------------
def main():
    setup_table()
    print("💰 Welcome to ATM System 💰")

    account = None
    while True:
        print("\nChoose an option:")
        print("1) Create Account")
        print("2) Login")
        print("3) Deposit")
        print("4) Withdraw")
        print("5) Check Balance")
        print("6) Exit")
        choice = input("Your choice (1-6): ").strip()

        if choice == "1":
            create_account()
        elif choice == "2":
            account = login()
        elif choice == "3":
            if account:
                amount = input("Enter deposit amount: ").strip()
                if amount.isdigit():
                    print(account.deposit(float(amount)))
                    update_balance(account)
                else:
                    print("Invalid amount.")
            else:
                print("Login first.")
        elif choice == "4":
            if account:
                amount = input("Enter withdrawal amount: ").strip()
                if amount.isdigit():
                    print(account.withdraw(float(amount)))
                    update_balance(account)
                else:
                    print("Invalid amount.")
            else:
                print("Login first.")
        elif choice == "5":
            if account:
                print(f"Current balance: ₹{account.get_balance()}")
            else:
                print("Login first.")
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Choose 1-6.")

if __name__ == "__main__":
    main()

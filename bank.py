import mysql.connector

# -------------------- Database Configuration --------------------
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "vishwa@12345"
DB_NAME = "dummy"
DB_PORT = 3306

def get_connection():
    """Establish and return a MySQL database connection."""
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

def setup_table():
    """Create the database and accounts table if they do not exist."""
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
            balance DECIMAL(15, 2) DEFAULT 0
        )
        """)
        conn.commit()
        cursor.close()
        conn.close()

# -------------------- BankAccount Class --------------------
class BankAccount:
    def __init__(self, account_holder, pin, balance=0.0):
        self.account_holder = account_holder
        self.__pin = pin
        self.__balance = balance  # float type

    def verify_pin(self, pin):
        """Verify whether the entered PIN matches the stored one."""
        return self.__pin == pin

    def deposit(self, amount):
        """Deposit a valid amount to the account."""
        if amount > 0:
            self.__balance += amount
            return f"Deposited ₹{amount:.2f}. New balance: ₹{self.__balance:.2f}"
        else:
            return "Invalid deposit amount."

    def withdraw(self, amount):
        """Withdraw a valid amount if sufficient funds are available."""
        if amount <= 0:
            return "Invalid withdrawal amount."
        elif amount > self.__balance:
            return "Insufficient funds."
        else:
            self.__balance -= amount
            return f"Withdrew ₹{amount:.2f}. Remaining balance: ₹{self.__balance:.2f}"

    def get_balance(self):
        """Return the current account balance."""
        return self.__balance

# -------------------- CRUD Operations --------------------
def create_account():
    """Create a new account if the account holder name does not already exist."""
    name = input("Enter account holder name: ").strip()
    pin = input("Set 4-digit PIN: ").strip()
    initial_balance = input("Initial deposit (number): ").strip()

    # Validate PIN length
    if not name or not pin.isdigit() or len(pin) != 4:
        print("Invalid input. Try again.")
        return

    # Validate and convert balance
    try:
        initial_balance = float(initial_balance)
    except ValueError:
        print("Invalid amount. Try again.")
        return

    conn = get_connection()
    if not conn:
        return

    cursor = conn.cursor()
    try:
        # Check if account already exists
        cursor.execute("SELECT 1 FROM accounts WHERE account_holder = %s LIMIT 1", (name,))
        exists = cursor.fetchone()

        if exists:
            print(f"Account with name '{name}' already exists. Please choose a different name.")
            return

        # Create new account
        cursor.execute(
            "INSERT INTO accounts (account_holder, pin, balance) VALUES (%s, %s, %s)",
            (name, pin, initial_balance)
        )
        conn.commit()
        print(f"Account created successfully for {name} with balance ₹{initial_balance:.2f}")

    except mysql.connector.Error as e:
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()

def login():
    """Login to an existing account after verifying the PIN."""
    name = input("Enter account holder name: ").strip()
    pin = input("Enter 4-digit PIN: ").strip()

    conn = get_connection()
    if not conn:
        return None

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM accounts WHERE account_holder = %s", (name,))
    account_info = cursor.fetchone()
    cursor.close()
    conn.close()

    if not account_info:
        print("Account not found.")
        return None

    # Convert balance from Decimal to float
    account = BankAccount(
        account_info['account_holder'],
        account_info['pin'],
        float(account_info['balance'])
    )

    if account.verify_pin(pin):
        print(f"Login successful. Welcome {account.account_holder}.")
        return account
    else:
        print("Incorrect PIN.")
        return None

def update_balance(account):
    """Update the account balance in the database."""
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE accounts SET balance = %s WHERE account_holder = %s",
        (account.get_balance(), account.account_holder)
    )
    conn.commit()
    cursor.close()
    conn.close()

# -------------------- Main Program --------------------
def main():
    setup_table()
    print("Welcome to the ATM System")

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
                try:
                    amount = float(amount)
                    print(account.deposit(amount))
                    update_balance(account)
                except ValueError:
                    print("Invalid amount. Please enter a valid number.")
            else:
                print("Please log in first.")
        elif choice == "4":
            if account:
                amount = input("Enter withdrawal amount: ").strip()
                try:
                    amount = float(amount)
                    print(account.withdraw(amount))
                    update_balance(account)
                except ValueError:
                    print("Invalid amount. Please enter a valid number.")
            else:
                print("Please log in first.")
        elif choice == "5":
            if account:
                print(f"Current balance: ₹{account.get_balance():.2f}")
            else:
                print("Please log in first.")
        elif choice == "6":
            print("Thank you for using the ATM System. Goodbye.")
            break
        else:
            print("Invalid choice. Please select a valid option (1–6).")

if __name__ == "__main__":
    main()

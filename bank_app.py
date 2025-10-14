import streamlit as st
import json
import os

DATA_FILE = "bank_data.json"

# -------------------- JSON Handling --------------------
def load_data():
    """Load account data from JSON file."""
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
        return data
    return {}

def save_data(data):
    """Save account data to JSON file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)


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

    def to_dict(self):
        """Convert account data to dictionary for saving."""
        return {
            "account_holder": self.account_holder,
            "pin": self._BankAccount__pin,
            "balance": self._BankAccount__balance
        }

    @classmethod
    def from_dict(cls, data):
        """Create BankAccount object from saved dictionary."""
        return cls(data["account_holder"], data["pin"], data["balance"])


# -------------------- Streamlit UI --------------------
st.set_page_config(page_title="💰 ATM System", page_icon="🏦")
st.title("🏦 ATM System")

# Load data from JSON file
accounts_data = load_data()

# Initialize session state
if "account" not in st.session_state:
    st.session_state.account = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_name" not in st.session_state:
    st.session_state.user_name = None

# Sidebar Menu
menu = st.sidebar.radio("📋 Menu", ["Create Account", "Login", "ATM Operations"])

# -------------------- CREATE ACCOUNT --------------------
if menu == "Create Account":
    st.header("Step 1: Create Account")
    name = st.text_input("Enter account holder name:")
    pin = st.text_input("Set 4-digit PIN", type="password", max_chars=4)
    initial_balance = st.number_input("Initial Deposit (₹)", min_value=0, step=100)

    if st.button("Create Account"):
        if not name.strip():
            st.warning("Enter a valid name.")
        elif not pin.isdigit() or len(pin) != 4:
            st.warning("PIN must be a 4-digit number.")
        elif name in accounts_data:
            st.error("Account with this name already exists. Try another name.")
        else:
            new_account = BankAccount(name.strip(), pin, initial_balance)
            accounts_data[name] = new_account.to_dict()
            save_data(accounts_data)
            st.success(f"Account created successfully for {name} with ₹{initial_balance}")
            st.info("Go to 'Login' page from the sidebar to access ATM services.")

# -------------------- LOGIN --------------------
elif menu == "Login":
    st.header("Step 2: Login to Your Account")

    if not accounts_data:
        st.warning("No accounts found. Please create one first.")
    else:
        name = st.text_input("Enter account holder name:")
        entered_pin = st.text_input("Enter your 4-digit PIN", type="password", max_chars=4)

        if st.button("Login"):
            if name not in accounts_data:
                st.error("Account not found. Please check your name.")
            else:
                account_info = accounts_data[name]
                account = BankAccount.from_dict(account_info)
                if account.verify_pin(entered_pin):
                    st.session_state.account = account
                    st.session_state.logged_in = True
                    st.session_state.user_name = name
                    st.success(f"Welcome {account.account_holder}! Login successful.")
                    st.info("Go to 'ATM Operations' page to perform transactions.")
                else:
                    st.error("Incorrect PIN. Try again.")

# -------------------- ATM OPERATIONS --------------------
elif menu == "ATM Operations":
    st.header("ATM Operations")

    if not st.session_state.logged_in or st.session_state.account is None:
        st.warning("Please log in first from the 'Login' page.")
    else:
        account = st.session_state.account
        name = st.session_state.user_name

        action = st.radio("Choose an action", ["Deposit", "Withdraw", "Check Balance"])

        if action == "Deposit":
            amount = st.number_input("Enter deposit amount (₹)", min_value=0, step=100, key="dep")
            if st.button("Deposit"):
                message = account.deposit(amount)
                st.info(message)
                accounts_data[name] = account.to_dict()
                save_data(accounts_data)

        elif action == "Withdraw":
            amount = st.number_input("Enter withdrawal amount (₹)", min_value=0, step=100, key="with")
            if st.button("Withdraw"):
                message = account.withdraw(amount)
                st.info(message)
                accounts_data[name] = account.to_dict()
                save_data(accounts_data)

        elif action == "Check Balance":
            st.success(f"Your current balance is ₹{account.get_balance()}")

        st.divider()
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.account = None
            st.success("Logged out successfully.")

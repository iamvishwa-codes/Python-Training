import streamlit as st

# ---------- BankAccount Class ----------
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
            return f"✅ Deposited ₹{amount}. New balance: ₹{self.__balance}"
        else:
            return "⚠️ Invalid deposit amount."

    def withdraw(self, amount):
        if amount <= 0:
            return "⚠️ Invalid withdrawal amount."
        elif amount > self.__balance:
            return "❌ Insufficient funds."
        else:
            self.__balance -= amount
            return f"✅ Withdrew ₹{amount}. Remaining balance: ₹{self.__balance}"

    def get_balance(self):
        return self.__balance


# ---------- Streamlit UI ----------
st.set_page_config(page_title="ATM System", page_icon="💰")
st.title("🏦 ATM System")

# Initialize session state
if "account" not in st.session_state:
    st.session_state.account = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Sidebar Navigation
menu = st.sidebar.radio("📋 Menu", ["Create Account", "Login", "ATM Operations"])

# ---------- CREATE ACCOUNT ----------
if menu == "Create Account":
    st.header("🆕 Step 1: Create Account")

    name = st.text_input("Enter account holder name:")
    pin = st.text_input("Set 4-digit PIN", type="password", max_chars=4)
    initial_balance = st.number_input("Initial Deposit", min_value=0, step=100)

    if st.button("Create Account"):
        if not name.strip():
            st.warning("Please enter a valid name.")
        elif not pin.isdigit() or len(pin) != 4:
            st.warning("PIN must be a 4-digit number.")
        else:
            st.session_state.account = BankAccount(name.strip(), pin, initial_balance)
            st.success(f"🎉 Account created successfully for {name} with ₹{initial_balance}!")
            st.info("Go to the 'Login' page to access your ATM account.")

# ---------- LOGIN PAGE ----------
elif menu == "Login":
    st.header("🔐 Step 2: Login to Your Account")

    if st.session_state.account is None:
        st.warning("No account found. Please create one first.")
    else:
        entered_pin = st.text_input("Enter your 4-digit PIN", type="password", max_chars=4)

        if st.button("Login"):
            if st.session_state.account.verify_pin(entered_pin):
                st.session_state.logged_in = True
                st.success(f"✅ Welcome {st.session_state.account.account_holder}! Login successful.")
                st.info("Go to 'ATM Operations' to perform transactions.")
            else:
                st.error("❌ Incorrect PIN. Please try again.")

# ---------- ATM OPERATIONS ----------
elif menu == "ATM Operations":
    st.header("💳 Step 3: ATM Operations")

    if not st.session_state.logged_in:
        st.warning("Please log in first from the 'Login' page.")
    elif st.session_state.account is None:
        st.warning("No active account. Please create one first.")
    else:
        action = st.radio("Choose an action", ["Deposit", "Withdraw", "Check Balance"])

        if action == "Deposit":
            amount = st.number_input("Enter deposit amount", min_value=0, step=100, key="dep")
            if st.button("Deposit"):
                st.info(st.session_state.account.deposit(amount))

        elif action == "Withdraw":
            amount = st.number_input("Enter withdrawal amount", min_value=0, step=100, key="with")
            if st.button("Withdraw"):
                st.info(st.session_state.account.withdraw(amount))

        elif action == "Check Balance":
            st.success(f"💰 Your current balance is ₹{st.session_state.account.get_balance()}")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.success("🚪 Logged out successfully.")

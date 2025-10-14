import streamlit as st

# -------------------------------
# Vehicle Classes
# -------------------------------

class Vehicle:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model

    def start(self):
        return f"{self.brand} {self.model} is starting 🚗"

class Car(Vehicle):
    def play_music(self):
        return f"{self.brand} {self.model} is playing music 🎵"

class ElectricCar(Car):
    def charge(self):
        return f"{self.brand} {self.model} is charging ⚡"

class SmartDevice:
    def connect_wifi(self):
        return "Connecting to WiFi 📶"

class SmartCar(Car, SmartDevice):
    def autopilot(self):
        return f"{self.brand} {self.model} AutoPilot Activated 🤖"

class Bike(Vehicle):
    def kick_start(self):
        return f"{self.brand} {self.model} kick-started 🏍️"

class ElectricSmartCar(SmartCar, ElectricCar):
    pass  # Inherits all methods from SmartCar + ElectricCar

# -------------------------------
# Streamlit UI
# -------------------------------

st.title("🚘 Vehicle Management System")

brand = st.text_input("Enter Vehicle Brand", "Tesla")
model = st.text_input("Enter Vehicle Model", "Model S")

vehicle_type = st.selectbox(
    "Select Vehicle Type",
    ["Car", "Bike", "Electric Car", "Smart Car", "Electric Smart Car"]
)

if st.button("Create Vehicle"):
    # Instantiate vehicle
    if vehicle_type == "Car":
        vehicle = Car(brand, model)
    elif vehicle_type == "Bike":
        vehicle = Bike(brand, model)
    elif vehicle_type == "Electric Car":
        vehicle = ElectricCar(brand, model)
    elif vehicle_type == "Smart Car":
        vehicle = SmartCar(brand, model)
    elif vehicle_type == "Electric Smart Car":
        vehicle = ElectricSmartCar(brand, model)
    else:
        st.error("Invalid vehicle type")
        st.stop()

    # Collect features dynamically
    features = []
    for method_name in ["start", "play_music", "connect_wifi", "autopilot", "charge", "kick_start"]:
        if hasattr(vehicle, method_name):
            method = getattr(vehicle, method_name)
            features.append({"Feature": method()})

    st.success(f"{vehicle_type}: {vehicle.brand} {vehicle.model}")
    st.table(features)

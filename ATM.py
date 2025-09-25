correct_pin = "1234"

while True:
    pin = input("Enter ATM PIN: ")
    if pin == correct_pin:
        print("PIN accepted. Welcome!")
        break
    else:
        print("Incorrect PIN. Try again...\n")

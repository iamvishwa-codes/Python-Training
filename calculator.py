def calculator():
    print("\nSelect operation:")
    print("1. Addition")
    print("2. Subtraction")
    print("3. Multiplication")
    print("4. Division")

    choice = input("Enter choice (1/2/3/4): ")

    num1 = float(input("Enter first number: "))
    num2 = float(input("Enter second number: "))

    if choice == '1':
        print("Result:", num1 + num2)
    elif choice == '2':
        print("Result:", num1 - num2)
    elif choice == '3':
        print("Result:", num1 * num2)
    elif choice == '4':
        if num2 != 0:
            print("Result:", num1 / num2)
        else:
            print("Error! Division by zero is not allowed.")
    else:
        print("Invalid input!")

    # Ask if the user wants to continue
    again = input("Do you want to calculate again? (yes/no): ").lower()
    if again == "yes":
        calculator()  # call the function again
    else:
        print("Program finished. Goodbye!")

# Start the calculator
calculator()

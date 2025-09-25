import random

print("🎲 Welcome to the Random Number Guessing Game!")
print("I'm thinking of a number between 1 and 100.")
print("You have 10 attempts to guess it.")

number_to_guess = random.randint(1, 100)

for attempt in range(1, 11):
    guess = int(input(f"Attempt {attempt}: Enter your guess: "))

    if guess < number_to_guess:
        print("Too low.")
    elif guess > number_to_guess:
        print("Too high.")
    else:
        print(f"🎉 Correct! You guessed it in {attempt} attempts.")
        break
else:
    print(f"❌ Sorry, you've used all attempts. The number was {number_to_guess}.")

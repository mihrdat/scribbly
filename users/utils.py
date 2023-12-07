import random


def generate_random_username():
    # Generate a random 8-digit number
    choices = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    random_number = "".join(random.choices(choices, k=8))

    # Create the username by concatenating the prefix and the random number
    username = f"U-{random_number}"

    return username

import random
import string


def generate_random_room_name():
    # Generate a random 32-digit string
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choices(characters, k=32))

    return f"R-{random_string}"

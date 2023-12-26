import random
import string


def generate_random_room_name():
    # Generate a random 8-digit string
    characters = string.ascii_letters + string.digits
    random_string = "".join(random.choices(characters, k=8))

    # Create the room name by concatenating the prefix and the random string
    room_name = f"R-{random_string}"

    return room_name

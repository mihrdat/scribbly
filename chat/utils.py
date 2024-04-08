import uuid


def generate_random_room_name():
    return f"R-{uuid.uuid4()}"

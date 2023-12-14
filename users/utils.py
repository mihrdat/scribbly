import random
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode


def encode_uid(pk):
    return force_str(urlsafe_base64_encode(force_bytes(pk)))


def decode_uid(pk):
    return force_str(urlsafe_base64_decode(pk))


def generate_random_username():
    # Generate a random 8-digit number
    choices = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    random_number = "".join(random.choices(choices, k=8))

    # Create the username by concatenating the prefix and the random number
    username = f"U-{random_number}"

    return username


def generate_random_code(number_of_digits=5):
    choices = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]
    return "".join(random.choices(choices, k=number_of_digits))

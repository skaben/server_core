import string
import random
from django.contrib.auth import get_user_model


def gen_random_str(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choices(chars, k=size))


def create_user(**params):
    return get_user_model().objects.create_user(**params)

import string
import random


def gen_random_str(size=8, chars=string.ascii_lowercase + string.digits):
    return ''.join(random.choices(chars, k=size))

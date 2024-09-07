import random
import string


def random_string(num):
    random_list = [random.choice(string.ascii_letters + string.digits) for i in range(num)]
    return "".join(random_list)

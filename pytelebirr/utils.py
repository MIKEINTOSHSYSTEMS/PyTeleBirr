import random
from typing import Union


def password_fixer(
        password: Union[int, str]
):
    last_n = list(str(password)[-2:])
    last_n.reverse()
    return str(random.randint(1, 9)) + str(password)[:-2] + str("".join(last_n)) + str(random.randint(1, 9))

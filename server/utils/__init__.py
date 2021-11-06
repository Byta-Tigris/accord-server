from hashlib import sha256
from datetime import datetime



"""
Generates account id for new user using their email id and datetime of creation
"""
def account_id_generator(email: str, time: datetime) -> str:
    time_in_string = f"{time.year}{time.month}{time.day}{time.second}{time.microsecond}"
    hash_algo = sha256()
    hash_algo.update(time_in_string.encode())
    return hash_algo.hexdigest()


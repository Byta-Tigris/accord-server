from hashlib import sha256
from datetime import datetime

from utils.errors import PasswordValidationError




def account_id_generator(email: str, entity_type: str) -> str:
    """Generate account hash using email and entity_type [Returns string]"""
    hash_algo = sha256()
    hash_algo.update(f"{email}__{entity_type}".encode())
    return hash_algo.hexdigest()



def validate_password(password: str) -> bool :
    """Password must be greater than 8 characters and less than 20, must have alphabets and numbers.\n
     special symbols are allowed are only allowed special characters\n
     raises PasswordValidationError if wrong\n
     Returns True"""
    if 7 < len(password) < 21 and any(char.isdigit() for char in password) and \
        any(char.isalpha()  for char in password):
        return True
    raise PasswordValidationError(password)

    
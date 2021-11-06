from hashlib import sha256
from datetime import datetime




def account_id_generator(email: str, entity_type: str) -> str:
    """Generate account hash using email and entity_type [Returns string]"""
    hash_algo = sha256()
    hash_algo.update(f"{email}__{entity_type}".encode())
    return hash_algo.hexdigest()


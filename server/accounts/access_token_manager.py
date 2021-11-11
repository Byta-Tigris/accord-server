from typing import List
from cryptography.fernet import Fernet, MultiFernet
import os


class AccessTokenManager:
    """Manages the encryption and decryption of access tokens for social media handles

    Wrapper for generating new keys, loading keys, encrypting and decrypting data
    """

    _fernet = None
    _keys = None

    def decrypt_acces_token(self, token: str) -> str:
        return self._decrypt(token)


    def _encrypt(self, data: str) -> str:
        return self.fernet.encrypt(data.encode()).decode()


    def _get_fernet_keys(self) -> List[str]:
        if self._keys and  len(self._keys) > 0:
            return self._keys
        return os.getenv("KEY_ARRAY","").split(" ")
    
    def get_fernet_keys(self, *keys) -> List[bytes]:
        return [key.encode() for key in self._get_fernet_keys()]

    @property
    def fernet(self) -> MultiFernet:
        keys = self.get_fernet_keys()
        if self._fernet == None or len(keys) != len(self._fernet._fernets):
            self._fernet = MultiFernet(keys)
        return self._fernet

    def encrypt_access_token(self, token: str) -> str:
        return self._encrypt(token)

    def _decrypt(self, data: str) -> str:
        return self.fernet.decrypt(data.encode()).decode()

    @staticmethod
    def generate_new_key() -> str:
        return Fernet.generate_key().decode()

    def rotate_token(self, token: str) -> str:
        return self.fernet.rotate(token.encode()).decode()




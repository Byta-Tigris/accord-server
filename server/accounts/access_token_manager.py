from typing import List, Callable, Union
from cryptography.fernet import Fernet, MultiFernet
import os


class AccessTokenManager:
    """Manages the encryption and decryption of access tokens for social media handles

    Wrapper for generating new keys, loading keys, encrypting and decrypting data
    """

    _fernet = None
    _keys = None

    _instance = None

    def decrypt_acces_token(self, token: str) -> str:
        return self._decrypt(token)


    def _encrypt(self, data: str) -> str:
        return self.wrapper_runner(self.fernet.encrypt, data)
    

    def wrapper_runner(self,fn: Callable, arg: str) -> str:
        return self._transfrom_to_str(fn(self._transfrom_to_bytes(arg)[0]))[0]
    

    @staticmethod
    def _transfrom_to_bytes(*args: List[Union[str, bytes]]) -> List[bytes]:
        args = list(args)
        for index, string in enumerate(args):
            if isinstance(string, str):
                args[index] = string.encode()
        return args
    
    @staticmethod
    def _transfrom_to_str(*args: List[Union[str, bytes]]) -> List[str]:
        args = list(args)
        for index, bytes_data in enumerate(args):
            if isinstance(bytes_data, bytes):
                args[index] = bytes_data.decode()
        return args


    def _get_fernet_keys(self) -> List[str]:
        if self._keys and  len(self._keys) > 0:
            return self._keys
        return os.getenv("KEY_ARRAY","").split(" ")
    
    def get_fernet_keys(self) -> List[bytes]:
        return self._transfrom_to_bytes(*self._get_fernet_keys())

    @property
    def fernet(self) -> MultiFernet:
        key_fernets = [Fernet(key) for key in self.get_fernet_keys()]
        if self._fernet == None or len(key_fernets) != len(self._fernet._fernets):
            self._fernet = MultiFernet(key_fernets)
        return self._fernet

    def encrypt_access_token(self, token: str) -> str:
        return self._encrypt(token)

    def _decrypt(self, data: str) -> str:
        return self.wrapper_runner(self.fernet.decrypt, data)

    @staticmethod
    def generate_new_key() -> str:
        return AccessTokenManager._transfrom_to_str(Fernet.generate_key())[0]

    def rotate_token(self, token: str) -> str:
        return self.wrapper_runner(self.fernet.rotate, token)




from unittest import TestCase

from cryptography.fernet import MultiFernet
from accounts.access_token_manager import AccessTokenManager


class TestAccessTokenManager(TestCase):
    
    def setUp(self) -> None:
        self.token_manager = AccessTokenManager()
        self.keys = []
    
    def test_generate_new_key(self):
        keys = []
        for i in range(0,10):
            key = self.token_manager.generate_new_key()
            self.assertNotEqual(len(key) , 0)
            self.assertNotIn(key, keys)
            keys.append(key)
        self.keys = keys
    
    def test_get_fernet_keys(self):
        if len(self.keys) == 0:
            self.keys = [self.token_manager.generate_new_key() for i in range(0,10)]
        keys = self.token_manager.get_fernet_keys(*self.keys)
        for key in keys:
            self.assertIsInstance(key, bytes)
    
    def test_fernet(self):
        if len(self.keys) == 0:
            self.keys = [self.token_manager.generate_new_key() for i in range(0,10)]
        keys = self.keys
        self.token_manager._keys = keys
        fernet = self.token_manager.fernet
        
        self.assertIsInstance(fernet, MultiFernet)
        n_keys = len(fernet._fernets)
        self.assertEqual(n_keys, len(keys))
        keys  = keys[:-1]
        self.token_manager._keys = keys
        self.assertNotEqual(len(self.token_manager.fernet._fernets), n_keys)
    
    def test_encrypt(self):
        pass

    def test_decrypt(self):
        pass
import os
from typing import Optional
from cryptography.fernet import Fernet
import logging

logger = logging.getLogger(__name__)

class KeysManager:
    @staticmethod
    def _save_encrypted_key(provider: str, api_key: str):
        """Save the API key securely using encryption."""
        key_path = os.path.expanduser(f"~/.{provider}_key")
        encryption_key = Fernet.generate_key()
        cipher_suite = Fernet(encryption_key)
        encrypted_key = cipher_suite.encrypt(api_key.encode())
    
        with open(key_path, 'wb') as f:
            f.write(encryption_key + b'\\n' + encrypted_key)
    
    @staticmethod
    def _load_encrypted_key(provider: str) -> Optional[str]:
        """Load and decrypt the API key."""
        key_path = os.path.expanduser(f"~/.{provider}_key")
        if not os.path.exists(key_path):
            return None
    
        try:
            with open(key_path, 'rb') as f:
                encryption_key, encrypted_key = f.read().split(b'\\n')
                cipher_suite = Fernet(encryption_key)
                return cipher_suite.decrypt(encrypted_key).decode()
        except Exception as e:
            logger.error(f"Failed to load or decrypt API key for {provider}: {e}")
            return None


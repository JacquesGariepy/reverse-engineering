import os
from cryptography.fernet import Fernet
from .exceptions import ReverseEngineerError
import logging

logger = logging.getLogger(__name__)

class KeyManager:
    @staticmethod
    def save_encrypted_key(provider: str, api_key: str):
        """Save the API key securely using encryption."""
        key_path = os.path.expanduser(f"~/.{provider}_key")
        encryption_key = Fernet.generate_key()
        cipher_suite = Fernet(encryption_key)
        encrypted_key = cipher_suite.encrypt(api_key.encode())
    
        with open(key_path, 'wb') as f:
            f.write(encryption_key + b'\\n' + encrypted_key)
    
    @staticmethod
    def load_encrypted_key(provider: str) -> Optional[str]:
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
    
    def setup_api_keys(self):
        """Set up API keys for different providers."""
        providers = set(model.provider for model in self.models.values())
        for provider in providers:
            env_var = f"{provider.upper()}_API_KEY"
            api_key = self._load_encrypted_key(provider.lower())
    
            if not api_key:  # If no saved key was found, ask the user
                api_key = os.getenv(env_var)
                if not api_key:
                    api_key = self.io.input(f"Please enter your {provider} API key: ", password=True)
                    os.environ[env_var] = api_key
                    
                    save_key = self.io.confirm(f"Do you want to save this {provider} API key for future sessions?")
                    if save_key:
                        self._save_encrypted_key(provider.lower(), api_key)
            else:
                os.environ[env_var] = api_key


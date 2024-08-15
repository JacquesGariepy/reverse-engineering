
# Expose key classes and modules for easier access when importing the package

from .reverse_engineer import ReverseEngineer
from .exceptions import ReverseEngineerError
from .config import Config, ModelConfig
from .utils import (
    read_file,
    _is_url,
    _read_local_file,
    _read_url
)
from .llm_manager import LLMManager
from .keys_manager import KeyManager

__all__ = [
    "ReverseEngineer",
    "ReverseEngineerError",
    "Config",
    "ModelConfig",
    "read_file",
    "_is_url",
    "_read_local_file",
    "_read_url",
    "LLMManager",
    "KeyManager"
]

# Version of the reverse_engineer package
__version__ = "0.1.0"

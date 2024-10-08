#__init__.py
# init file

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
from .keys_manager import KeysManager

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
    "KeysManager"
]

# Version of the reverse_engineer package
__version__ = "0.1.0"

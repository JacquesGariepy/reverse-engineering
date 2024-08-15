import os
import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def read_file(file_path: str) -> str:
    """Read code from a local file or URL."""
    if _is_url(file_path):
        return _read_url(file_path)
    else:
        return _read_local_file(file_path)

def _is_url(path: str) -> bool:
    """Check if the given path is a URL."""
    from urllib.parse import urlparse
    try:
        result = urlparse(path)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def _read_local_file(file_path: str) -> str:
    """Read code from a local file."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except IOError as e:
        logger.error(f"Error reading file: {e}")
        raise Exception(f"Error reading file: {str(e)}")

def _read_url(url: str) -> str:
    """Read code from a URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logger.error(f"Error fetching URL: {e}")
        raise Exception(f"Error fetching URL: {str(e)}")

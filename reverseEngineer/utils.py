import os
import re
import shlex
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

def handle_windows_paths(command):
    # Regex to match quoted paths with backslashes
    path_pattern = r'"([^"]*(\\\s+[^"]*)*)"'
    
    def replace_backslashes(match):
        # Replace backslashes with forward slashes in the matched path
        return '"' + match.group(1).replace('\\', '/') + '"'
    
    # Replace backslashes with forward slashes in quoted paths
    processed_command = re.sub(path_pattern, replace_backslashes, command)
    
    return processed_command

def process_command(command):
    # Pre-process the command to handle Windows paths
    processed_command = handle_windows_paths(command)
    
    # Use shlex.split() on the processed command
    return shlex.split(processed_command)
#reverse_engineer.py

import os
import sys
from typing import Dict, Any, Optional, List, Union
import requests
from urllib.parse import urlparse
import typer
from enum import Enum
from datetime import datetime
import json
import ast
import re
from functools import lru_cache, wraps
import time
import logging
from dotenv import load_dotenv
import yaml
from pydantic import BaseModel, Field
from aider import models, prompts, coders, io
from cryptography.fernet import Fernet  # Added for encryption
from config import Config
from exceptions import ReverseEngineerError
from keys_manager import KeysManager
from llm_manager import LLMManager

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    CSHARP = "csharp"
    RUBY = "ruby"
    GO = "go"
    RUST = "rust"
    SWIFT = "swift"
    PHP = "php"
    ASSEMBLY = "assembly"
    UNKNOWN = "unknown"

class ReverseEngineer:
    def __init__(self, config_path: str = None):
        """
        Initialize the ReverseEngineer class.

        Args:
            config_path (str): Path to the configuration file.
        """
        self.config_path = config_path or os.getenv("REVERSE_ENGINEER_CONFIG_PATH", "config.yaml")
        self.config = self._load_config(self.config_path)
        self.default_model = self.config.default_model
        self.models = self.config.models
        self.rate_limit = self.config.rate_limit
        self.keys_manager = KeysManager()
        # Set up API keys for different providers
        self.setup_api_keys()

        # Initialize rate limiting
        self.rate_limit_state = {'tokens': 0, 'last_reset': time.time()}

        # Initialize aider components
        self.io = io.InputOutput()
        self.llm_manager = LLMManager(self.config)

    def _load_config(self, config_path: str) -> Config:
        """Load configuration from a YAML file."""
        try:
            with open(config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            return Config(**config_dict)
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise ReverseEngineerError(f"Error loading configuration: {str(e)}")
        
    def setup_api_keys(self):
        """Set up API keys for different providers."""
        providers = set(model.provider for model in self.models.values())
        for provider in providers:
            env_var = f"{provider.upper()}_API_KEY"
            api_key = self.keys_manager._load_encrypted_key(provider.lower())
    
            if not api_key:  # If no saved key was found, ask the user
                api_key = os.getenv(env_var)
                if not api_key:
                    api_key = self.io.input(f"Please enter your {provider} API key: ", password=True)
                    os.environ[env_var] = api_key
                    
                    save_key = self.io.confirm(f"Do you want to save this {provider} API key for future sessions?")
                    if save_key:
                        self.keys_manager._save_encrypted_key(provider.lower(), api_key)
            else:
                os.environ[env_var] = api_key

    def _check_rate_limit(self):
        """Check if the current operation would exceed the rate limit."""
        current_time = time.time()
        if current_time - self.rate_limit_state['last_reset'] > self.rate_limit['time_frame']:
            self.rate_limit_state['tokens'] = 0
            self.rate_limit_state['last_reset'] = current_time
        
        if self.rate_limit_state['tokens'] >= self.rate_limit['limit']:
            wait_time = self.rate_limit['time_frame'] - (current_time - self.rate_limit_state['last_reset'])
            raise ReverseEngineerError(f"Rate limit exceeded. Please wait {wait_time:.2f} seconds before trying again.")

    def _update_rate_limit(self, tokens: int):
        """Update the rate limit counter."""
        self.rate_limit_state['tokens'] += tokens

    @lru_cache(maxsize=100)
    def _get_completion(self, prompt: str, model_name: str) -> str:
        """
        Get a completion from the specified AI model using aider.

        This method is cached to reduce redundant API calls. It also implements
        rate limiting and retry logic for robustness.
        """
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self._check_rate_limit()
                self.coder = self.llm_manager.coders[model_name]
                response = self.coder.run(prompt)
                self._update_rate_limit(len(response.split()))  # Approximation of token count
                return response
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    raise ReverseEngineerError(f"Error in API call after {max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff

    def analyze(self, code: str, language: Language, model_name: Optional[str] = None) -> str:
        """Analyze the given code using aider."""
        model_name = model_name or self.default_model
        prompt = f"Analyze the following {language.value} code:\n\n{code}\n\nProvide a detailed analysis of its functionality, design choices, and interactions."
        return self._get_completion(prompt, model_name)

    def identify_issues(self, code: str, language: Language, model_name: Optional[str] = None) -> str:
        """Identify potential issues in the given code using aider."""
        model_name = model_name or self.default_model
        prompt = f"Identify potential issues, vulnerabilities, or areas for improvement in the following {language.value} code:\n\n{code}"
        return self._get_completion(prompt, model_name)

    def optimize(self, code: str, language: Language, model_name: Optional[str] = None) -> str:
        """Suggest optimizations for the given code using aider."""
        model_name = model_name or self.default_model
        prompt = f"Suggest improvements to optimize performance and security for the following {language.value} code:\n\n{code}"
        return self._get_completion(prompt, model_name)

    def generate_documentation(self, code: str, language: Language, model_name: Optional[str] = None) -> str:
        """Generate documentation for the given code using aider."""
        model_name = model_name or self.default_model
        prompt = f"Generate comprehensive documentation for the following {language.value} code:\n\n{code}\n\nInclude function/method descriptions, parameters, return values, and overall purpose."
        return self._get_completion(prompt, model_name)

    def refactor(self, code: str, language: Language, model_name: Optional[str] = None) -> str:
        """Suggest refactoring improvements for the given code using aider."""
        model_name = model_name or self.default_model
        prompt = f"Suggest refactoring improvements for the following {language.value} code to enhance readability, maintainability, and adherence to best practices:\n\n{code}"
        return self._get_completion(prompt, model_name)

    def explain_algorithm(self, code: str, language: Language, model_name: Optional[str] = None) -> str:
        """Explain the algorithm used in the given code using aider."""
        model_name = model_name or self.default_model
        prompt = f"Explain the algorithm(s) used in the following {language.value} code in detail:\n\n{code}\n\nDescribe the approach, time complexity, and space complexity if applicable."
        return self._get_completion(prompt, model_name)

    def generate_test_cases(self, code: str, language: Language, model_name: Optional[str] = None) -> str:
        """Generate test cases for the given code using aider."""
        model_name = model_name or self.default_model
        prompt = f"Generate comprehensive test cases for the following {language.value} code:\n\n{code}\n\nInclude normal cases, edge cases, and potential error scenarios."
        return self._get_completion(prompt, model_name)

    def identify_design_patterns(self, code: str, language: Language, model_name: Optional[str] = None) -> str:
        """Identify design patterns used in the given code using aider."""
        model_name = model_name or self.default_model
        prompt = f"Identify and explain any design patterns used in the following {language.value} code:\n\n{code}\n\nDescribe how each pattern is implemented and its purpose in the code."
        return self._get_completion(prompt, model_name)

    def convert_language(self, code: str, from_language: Language, to_language: Language, model_name: Optional[str] = None) -> str:
        """Convert the given code from one programming language to another using aider."""
        model_name = model_name or self.default_model
        prompt = f"Convert the following {from_language.value} code to {to_language.value}:\n\n{code}\n\nEnsure that the functionality remains the same and adhere to the best practices of the target language."
        return self._get_completion(prompt, model_name)

    def security_audit(self, code: str, language: Language, model_name: Optional[str] = None) -> str:
        """Perform a security audit on the given code using aider."""
        model_name = model_name or self.default_model
        prompt = f"Perform a comprehensive security audit on the following {language.value} code:\n\n{code}\n\nIdentify potential security vulnerabilities, suggest fixes, and explain the implications of each issue."
        return self._get_completion(prompt, model_name)

    def save_output(self, output: str, command: str, file: str, output_dir: str = None, filename: Optional[str] = None):
        """Save the output to a file."""
        output_dir = output_dir or os.getenv("REVERSE_ENGINEER_OUTPUT_DIR", "output")
        os.makedirs(output_dir, exist_ok=True)
        
        base_name = os.path.basename(file)
        file_name, _ = os.path.splitext(base_name)
        
        if filename:
            output_file = f"{filename}.txt"
            full_path = os.path.join(output_dir, output_file)
            iteration = 1
            while os.path.exists(full_path):
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_file = f"{filename}_{iteration}_{timestamp}.txt"
                full_path = os.path.join(output_dir, output_file)
                iteration += 1
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"{file_name}_{command}_{timestamp}.txt"
            full_path = os.path.join(output_dir, output_file)
        
        with open(full_path, 'w') as f:
            f.write(output)
        
        return full_path

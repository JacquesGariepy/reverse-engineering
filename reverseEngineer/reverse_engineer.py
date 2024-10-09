#reverse_engineer.py

import math
import os
import sys
from typing import Dict, Any, Optional, List, Union
import autogen
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
from static_analysis import StaticAnalyzer

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

    def analyze(self, file_path: str, code: str, language: str, model_name: Optional[str] = None, test_file_name: Optional[str] = None) -> str:
        """
        Analyze the code file using Aider and provide detailed recommendations based on static analysis.

        This function identifies issues using StaticAnalyzer and generates a prompt containing detailed
        recommendations for each issue, as well as optionally generating test cases based on the provided test file.

        Args:
            file_path: The path to the file containing the code to analyze (not the content of the code).
            code: The code to analyze.
            test_file_name: The name of the test file associated with the code (optional).
            language: The programming language of the code being analyzed.
            model_name: (Optional) The name of the model to use for LLM interactions.

        Returns:
            str: A string containing the detailed analysis and refactoring recommendations.
        """
        model_name = model_name or self.default_model

        # Step 1: Perform static analysis using StaticAnalyzer
        static_analyzer = StaticAnalyzer(file_path, code, test_file_name)
        issues = static_analyzer.analyze()

        # Step 2: Break down code into smaller chunks for multi-turn communication if necessary
        code_chunks = self._split_code_into_chunks(code)

        # Step 3 and 4: Construct the analysis prompt and include optional test generation instructions
        full_prompt = (
            f"Analyze the following source code written in {language}. The following issues were detected "
            f"during static analysis: {issues}. Please provide a detailed analysis of the identified issues " 
            f"along with specific recommendations for fixing them. Include a relevant code snippet for each "
            f"recommendation to demonstrate the solution. Do not include the original source code in your "
            f"response—focus solely on offering advice, solutions, and examples so the developer can make the corrections independently."
        )

        # If a test file is provided, include test generation instructions
        if test_file_name:
            full_prompt += (
                f"\n\nAdditionally, generate appropriate unit tests for the code based on the provided test file "
                f"'{test_file_name}'. Ensure the tests cover the refactored functionality, edge cases, and are structured "
                f"to follow best practices in testing."
            )

        # Step 5: Communicate with Aider incrementally over multiple turns if necessary
        response = ""
        for i, code_chunk in enumerate(code_chunks):
            chunk_prompt = full_prompt + f"\n\nCode chunk {i+1}/{len(code_chunks)}:\n\n{code_chunk}\n\n"
            response_chunk = self._get_completion(chunk_prompt, model_name)
            response += f"Response for chunk {i+1}/{len(code_chunks)}:\n{response_chunk}\n\n"

        return response

    def _split_code_into_chunks(self, code: str, max_tokens: int = 500) -> List[str]:
        """
        Split the code into smaller chunks that fit within the token limit of the model.

        Args:
            code (str): The source code to split.
            max_tokens (int): Maximum tokens allowed per chunk (adjust this based on model token limits).

        Returns:
            List[str]: List of code chunks.
        """
        lines = code.splitlines()
        chunk_size = math.ceil(len(lines) / (len(lines) // max_tokens + 1))
        return ['\n'.join(lines[i:i+chunk_size]) for i in range(0, len(lines), chunk_size)]

    def agent_config(self):
         return {
            "engineer": {
                "name": "engineer",
                "llm_config": {
                    "model": "gpt-4o",
                    "temperature": 0.3,
                    "seed": 10
                },
                "system_message": (
                    "You are Software Engineer. You follow an approved plan. You write python/shell code to solve tasks. "
                    "Wrap the code in a code block that specifies the script type. The user can't modify your code. "
                    "So do not suggest incomplete code which requires others to modify. Don't use a code block if it's not "
                    "intended to be executed by the executor. Don't include multiple code blocks in one response. Do not ask others "
                    "to copy and paste the result. Check the execution result returned by the executor. If the result indicates "
                    "there is an error, fix the error and output the code again. Suggest the full code instead of partial code or "
                    "code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, "
                    "analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try."
                )
            }
    }

    def _get_completion(self, prompt: str, model_name: str) -> str:
        """
        Get a completion from the specified AI model using Aider.

        This method is cached to reduce redundant API calls. It also implements
        rate limiting and retry logic for robustness.
        """
        from autogen.agentchat import AssistantAgent, UserProxyAgent
        max_retries = 3
        for attempt in range(max_retries):
            try:
                self._check_rate_limit()
                #self.coder = self.llm_manager.coders[model_name]
                #response = self.coder.run(prompt)
                config = self.agent_config()
                assistant = AssistantAgent(name="CodeAnalyzer", llm_config=config["engineer"]["llm_config"], system_message=config["engineer"]["system_message"])
                user_proxy = UserProxyAgent("user_proxy", code_execution_config={"executor": autogen.coding.LocalCommandLineCodeExecutor(work_dir="coding")}, human_input_mode="TERMINATE", max_consecutive_auto_reply=1)
                user_proxy.initiate_chat(assistant,message=prompt)
                response = user_proxy.send(
                        recipient=assistant,
                        message="exit")

                self._update_rate_limit(len(response.split()))  # Approximation of token count
                return response
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    raise ReverseEngineerError(f"Error in API call after {max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff


    def refactor(self, file_path: str, code: str, language: str, model_name: Optional[str] = None, test_file_name: Optional[str] = None) -> str:
        """
        Suggest refactoring improvements for the given code using aider, based on the issues detected during static analysis.

        This function leverages the static analysis issues to provide targeted refactorings aimed at improving
        readability, maintainability, and adherence to best practices.
        """
        model_name = model_name or self.default_model

        # Step 1: Perform static analysis to detect issues
        static_analyzer = StaticAnalyzer(file_path, code, test_file_name)
        issues = static_analyzer.analyze()
        # Step 2: Construct the refactor prompt, incorporating the issues detected
        prompt = (
            f"Refactor the following {language.value} code to address the following issues:\n\n"
            f"{code}\n\n"
            f"The following issues were detected during {issues}\n"
        )

        # Final instructions to refactor the code for improvements
        prompt += (
            "Please refactor the code to improve readability, maintainability, and adherence to best practices. "
            "Demonstrate mastery of the following concepts in your refactored code:\n\n"
            "SOLID Principles: Implement the Single Responsibility Principle (SRP), Open/Closed Principle (OCP), "
            "Liskov Substitution Principle (LSP), Interface Segregation Principle (ISP), and Dependency Inversion Principle (DIP).\n"
            "Clean Code: Ensure clear and meaningful naming of variables, functions, and classes; short, focused functions that do one thing; "
            "relevant and helpful comments; and consistent, readable code formatting.\n"
            "DRY: Avoid code duplication by using abstraction and modularity.\n"
            "KISS & YAGNI: Favor simple, understandable solutions and avoid unnecessary features.\n"
            "Separation of Concerns: Separate distinct responsibilities into different modules.\n"
            "Design Patterns: Apply appropriate design patterns to solve common problems.\n"
            "Test-Driven Development (TDD): Write tests before production code.\n"
            "Code Reviews: Actively participate in code reviews to ensure quality.\n"
            "Security Best Practices: Implement appropriate security measures.\n"
            "Performance Optimization: Optimize your code for better performance.\n"
            "Documentation: Provide clear and useful documentation for both the code and any APIs involved.\n\n"
            "As you refactor, explain your design choices, justify your implementation decisions, and demonstrate how you apply these concepts in practice."
        )

        # Step 3: Send the prompt to the LLM for code refactoring and return the result
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

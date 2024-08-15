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
from functools import lru_cache
import time
import logging
from dotenv import load_dotenv
import yaml
from pydantic import BaseModel, Field
from aider import models, prompts, coders, io

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

class ReverseEngineerError(Exception):
    """Custom exception for ReverseEngineer class"""
    pass

class ModelConfig(BaseModel):
    name: str
    provider: str
    api_base: Optional[str] = None
    max_tokens: int
    temperature: float = Field(0.7, ge=0.0, le=1.0)

class Config(BaseModel):
    default_model: str
    models: Dict[str, ModelConfig]
    rate_limit: Dict[str, Union[int, float]]

class ReverseEngineer:
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the ReverseEngineer class.

        Args:
            config_path (str): Path to the configuration file.
        """
        self.config = self._load_config(config_path)
        self.default_model = self.config.default_model
        self.models = self.config.models
        self.rate_limit = self.config.rate_limit

        # Set up API keys for different providers
        self._setup_api_keys()

        # Initialize rate limiting
        self.rate_limit_state = {'tokens': 0, 'last_reset': time.time()}

        # Initialize aider components
        self.io = io.InputOutput()
        self.llms = self._initialize_llms()
        self.coders = self._initialize_coders()

    def _load_config(self, config_path: str) -> Config:
        """Load configuration from a YAML file."""
        try:
            with open(config_path, 'r') as f:
                config_dict = yaml.safe_load(f)
            return Config(**config_dict)
        except Exception as e:
            raise ReverseEngineerError(f"Error loading configuration: {str(e)}")

    def _setup_api_keys(self):
        """Set up API keys for different providers."""
        providers = set(model.provider for model in self.models.values())
        for provider in providers:
            env_var = f"{provider.upper()}_API_KEY"
            api_key = os.getenv(env_var)
            if not api_key:
                api_key = self.io.input(f"Please enter your {provider} API key: ", password=True)
                os.environ[env_var] = api_key
                
                save_key = self.io.confirm(f"Do you want to save this {provider} API key for future sessions?")
                if save_key:
                    with open(os.path.expanduser(f"~/.{provider.lower()}_api_key"), "w") as f:
                        f.write(api_key)

    def _initialize_llms(self):
        """Initialize LLMs based on the configuration."""
        llms = {}
        for model_name, model_config in self.models.items():
            llm_class = getattr(models, f"{model_config.provider.capitalize()}Model")
            llms[model_name] = llm_class(
                model_name=model_name,
                api_key=os.getenv(f"{model_config.provider.upper()}_API_KEY"),
                api_base=model_config.api_base,
                temperature=model_config.temperature,
                max_tokens=model_config.max_tokens
            )
        return llms

    def _initialize_coders(self):
        """Initialize coders for each LLM."""
        return {model_name: coders.Coder(llm, self.io) for model_name, llm in self.llms.items()}

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
                coder = self.coders[model_name]
                response = coder.complete(prompt)
                self._update_rate_limit(len(response.split()))  # Approximation of token count
                return response
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    raise ReverseEngineerError(f"Error in API call after {max_retries} attempts: {str(e)}")
                time.sleep(2 ** attempt)  # Exponential backoff

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

    def read_file(self, file_path: str) -> str:
        """Read code from a local file or URL."""
        if self._is_url(file_path):
            return self._read_url(file_path)
        else:
            return self._read_local_file(file_path)

    def _is_url(self, path: str) -> bool:
        """Check if the given path is a URL."""
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def _read_local_file(self, file_path: str) -> str:
        """Read code from a local file."""
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except IOError as e:
            raise ReverseEngineerError(f"Error reading file: {str(e)}")

    def _read_url(self, url: str) -> str:
        """Read code from a URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            raise ReverseEngineerError(f"Error fetching URL: {str(e)}")

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

    def save_output(self, output: str, command: str, file: str, output_dir: str = "output", filename: Optional[str] = None):
        """Save the output to a file."""
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

# Typer CLI setup
app = typer.Typer()
re_engine = None

@app.command()
def init(config_path: str = typer.Option("config.yaml", help="Path to the configuration file")):
    """Initialize the ReverseEngineer tool with a configuration file."""
    global re_engine
    try:
        re_engine = ReverseEngineer(config_path)
        typer.echo(f"ReverseEngineer initialized with configuration from {config_path}")
    except ReverseEngineerError as e:
        typer.echo(f"Error initializing ReverseEngineer: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def analyze(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: Optional[str] = typer.Option(None, help="Specific model to use for analysis"),
    output: Optional[str] = typer.Option(None, help="Name of the output file (optional)")
):
    """Analyze the given code file."""
    if not re_engine:
        typer.echo("Please run 'init' command first to initialize the ReverseEngineer tool.")
        raise typer.Exit(code=1)
    
    try:
        code = re_engine.read_file(file)
        result = re_engine.analyze(code, language, model)
        if output:
            saved_path = re_engine.save_output(result, "analyze", file, filename=output)
            typer.echo(f"Output saved to: {saved_path}")
        else:
            typer.echo(result)
    except ReverseEngineerError as e:
        typer.echo(f"Error during analysis: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def identify_issues(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: Optional[str] = typer.Option(None, help="Specific model to use for analysis"),
    output: Optional[str] = typer.Option(None, help="Name of the output file (optional)")
):
    """Identify issues in the given code file."""
    if not re_engine:
        typer.echo("Please run 'init' command first to initialize the ReverseEngineer tool.")
        raise typer.Exit(code=1)
    
    try:
        code = re_engine.read_file(file)
        result = re_engine.identify_issues(code, language, model)
        if output:
            saved_path = re_engine.save_output(result, "identify_issues", file, filename=output)
            typer.echo(f"Output saved to: {saved_path}")
        else:
            typer.echo(result)
    except ReverseEngineerError as e:
        typer.echo(f"Error during issue identification: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def optimize(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: Optional[str] = typer.Option(None, help="Specific model to use for analysis"),
    output: Optional[str] = typer.Option(None, help="Name of the output file (optional)")
):
    """Suggest optimizations for the given code file."""
    if not re_engine:
        typer.echo("Please run 'init' command first to initialize the ReverseEngineer tool.")
        raise typer.Exit(code=1)
    
    try:
        code = re_engine.read_file(file)
        result = re_engine.optimize(code, language, model)
        if output:
            saved_path = re_engine.save_output(result, "optimize", file, filename=output)
            typer.echo(f"Output saved to: {saved_path}")
        else:
            typer.echo(result)
    except ReverseEngineerError as e:
        typer.echo(f"Error during optimization: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def generate_documentation(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: Optional[str] = typer.Option(None, help="Specific model to use for analysis"),
    output: Optional[str] = typer.Option(None, help="Name of the output file (optional)")
):
    """Generate documentation for the given code file."""
    if not re_engine:
        typer.echo("Please run 'init' command first to initialize the ReverseEngineer tool.")
        raise typer.Exit(code=1)
    
    try:
        code = re_engine.read_file(file)
        result = re_engine.generate_documentation(code, language, model)
        if output:
            saved_path = re_engine.save_output(result, "generate_documentation", file, filename=output)
            typer.echo(f"Output saved to: {saved_path}")
        else:
            typer.echo(result)
    except ReverseEngineerError as e:
        typer.echo(f"Error during documentation generation: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def refactor(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: Optional[str] = typer.Option(None, help="Specific model to use for analysis"),
    output: Optional[str] = typer.Option(None, help="Name of the output file (optional)")
):
    """Suggest refactoring improvements for the given code file."""
    if not re_engine:
        typer.echo("Please run 'init' command first to initialize the ReverseEngineer tool.")
        raise typer.Exit(code=1)
    
    try:
        code = re_engine.read_file(file)
        result = re_engine.refactor(code, language, model)
        if output:
            saved_path = re_engine.save_output(result, "refactor", file, filename=output)
            typer.echo(f"Output saved to: {saved_path}")
        else:
            typer.echo(result)
    except ReverseEngineerError as e:
        typer.echo(f"Error during refactoring: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def explain_algorithm(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: Optional[str] = typer.Option(None, help="Specific model to use for analysis"),
    output: Optional[str] = typer.Option(None, help="Name of the output file (optional)")
):
    """Explain the algorithm used in the given code file."""
    if not re_engine:
        typer.echo("Please run 'init' command first to initialize the ReverseEngineer tool.")
        raise typer.Exit(code=1)
    
    try:
        code = re_engine.read_file(file)
        result = re_engine.explain_algorithm(code, language, model)
        if output:
            saved_path = re_engine.save_output(result, "explain_algorithm", file, filename=output)
            typer.echo(f"Output saved to: {saved_path}")
        else:
            typer.echo(result)
    except ReverseEngineerError as e:
        typer.echo(f"Error during algorithm explanation: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def generate_test_cases(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: Optional[str] = typer.Option(None, help="Specific model to use for analysis"),
    output: Optional[str] = typer.Option(None, help="Name of the output file (optional)")
):
    """Generate test cases for the given code file."""
    if not re_engine:
        typer.echo("Please run 'init' command first to initialize the ReverseEngineer tool.")
        raise typer.Exit(code=1)
    
    try:
        code = re_engine.read_file(file)
        result = re_engine.generate_test_cases(code, language, model)
        if output:
            saved_path = re_engine.save_output(result, "generate_test_cases", file, filename=output)
            typer.echo(f"Output saved to: {saved_path}")
        else:
            typer.echo(result)
    except ReverseEngineerError as e:
        typer.echo(f"Error during test case generation: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def identify_design_patterns(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: Optional[str] = typer.Option(None, help="Specific model to use for analysis"),
    output: Optional[str] = typer.Option(None, help="Name of the output file (optional)")
):
    """Identify design patterns used in the given code file."""
    if not re_engine:
        typer.echo("Please run 'init' command first to initialize the ReverseEngineer tool.")
        raise typer.Exit(code=1)
    
    try:
        code = re_engine.read_file(file)
        result = re_engine.identify_design_patterns(code, language, model)
        if output:
            saved_path = re_engine.save_output(result, "identify_design_patterns", file, filename=output)
            typer.echo(f"Output saved to: {saved_path}")
        else:
            typer.echo(result)
    except ReverseEngineerError as e:
        typer.echo(f"Error during design pattern identification: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def convert_language(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    from_language: Language = typer.Option(..., help="Source programming language of the code"),
    to_language: Language = typer.Option(..., help="Target programming language for conversion"),
    model: Optional[str] = typer.Option(None, help="Specific model to use for analysis"),
    output: Optional[str] = typer.Option(None, help="Name of the output file (optional)")
):
    """Convert the given code file from one programming language to another."""
    if not re_engine:
        typer.echo("Please run 'init' command first to initialize the ReverseEngineer tool.")
        raise typer.Exit(code=1)
    
    try:
        code = re_engine.read_file(file)
        result = re_engine.convert_language(code, from_language, to_language, model)
        if output:
            saved_path = re_engine.save_output(result, f"convert_{from_language.value}_to_{to_language.value}", file, filename=output)
            typer.echo(f"Output saved to: {saved_path}")
        else:
            typer.echo(result)
    except ReverseEngineerError as e:
        typer.echo(f"Error during language conversion: {str(e)}", err=True)
        raise typer.Exit(code=1)

@app.command()
def security_audit(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: Optional[str] = typer.Option(None, help="Specific model to use for analysis"),
    output: Optional[str] = typer.Option(None, help="Name of the output file (optional)")
):
    """Perform a security audit on the given code file."""
    if not re_engine:
        typer.echo("Please run 'init' command first to initialize the ReverseEngineer tool.")
        raise typer.Exit(code=1)
    
    try:
        code = re_engine.read_file(file)
        result = re_engine.security_audit(code, language, model)
        if output:
            saved_path = re_engine.save_output(result, "security_audit", file, filename=output)
            typer.echo(f"Output saved to: {saved_path}")
        else:
            typer.echo(result)
    except ReverseEngineerError as e:
        typer.echo(f"Error during security audit: {str(e)}", err=True)
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()

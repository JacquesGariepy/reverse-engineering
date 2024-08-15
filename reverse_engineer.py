import os
import sys
from typing import Dict, Any, Optional, List
import litellm
import requests
from urllib.parse import urlparse
import typer
from enum import Enum
from datetime import datetime
import json
import ast
import re

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
    def __init__(self, default_model: str = "gpt-3.5-turbo"):
        self.api_key = os.getenv("OPENAI_API_KEY")
        litellm.api_key = self.api_key
        self.default_model = default_model
        self.max_tokens = 4096

    def _get_completion(self, prompt: str, model: Optional[str] = None) -> str:
        try:
            response = litellm.completion(
                model=model or self.default_model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            typer.echo(f"Error in API call: {str(e)}", err=True)
            sys.exit(1)

    def _chunk_code(self, code: str) -> List[str]:
        chunks = []
        current_chunk = ""
        for line in code.split("\n"):
            if len(current_chunk) + len(line) + 1 > self.max_tokens:
                chunks.append(current_chunk)
                current_chunk = line
            else:
                current_chunk += line + "\n"
        if current_chunk:
            chunks.append(current_chunk)
        return chunks

    def _analyze_chunks(self, chunks: List[str], model: Optional[str] = None) -> str:
        analyses = []
        for i, chunk in enumerate(chunks):
            prompt = f"Analyze the following code chunk ({i+1}/{len(chunks)}):\n\n{chunk}\n\nProvide a detailed analysis of its functionality, design choices, and interactions."
            analyses.append(self._get_completion(prompt, model))
        
        combined_analysis = "\n\n".join(analyses)
        summary_prompt = f"Summarize and combine the following analyses into a cohesive overview:\n\n{combined_analysis}"
        return self._get_completion(summary_prompt, model)

    def read_file(self, file_path: str) -> str:
        if self._is_url(file_path):
            return self._read_url(file_path)
        else:
            return self._read_local_file(file_path)

    def _is_url(self, path: str) -> bool:
        try:
            result = urlparse(path)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False

    def _read_local_file(self, file_path: str) -> str:
        try:
            with open(file_path, 'r') as file:
                return file.read()
        except IOError as e:
            typer.echo(f"Error reading file: {str(e)}", err=True)
            sys.exit(1)

    def _read_url(self, url: str) -> str:
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            typer.echo(f"Error fetching URL: {str(e)}", err=True)
            sys.exit(1)

    def analyze(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Analyze the following {language.value} code:\n\n{code}\n\nProvide a detailed analysis of its functionality, design choices, and interactions."
        return self._get_completion(prompt, model)

    def identify_issues(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Identify potential issues, vulnerabilities, or areas for improvement in the following {language.value} code:\n\n{code}"
        return self._get_completion(prompt, model)

    def optimize(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Suggest improvements to optimize performance and security for the following {language.value} code:\n\n{code}"
        return self._get_completion(prompt, model)

    def generate_report(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Generate a detailed report summarizing the analysis, identified issues, and recommendations for the following {language.value} code:\n\n{code}"
        return self._get_completion(prompt, model)

    def extract(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Extract and list the main functions, classes, and modules from this {language.value} code:\n\n{code}"
        return self._get_completion(prompt, model)

    def refactor(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Suggest refactoring improvements for this {language.value} code:\n\n{code}"
        return self._get_completion(prompt, model)

    def summarize(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Provide a concise summary of this {language.value} code, highlighting key parts:\n\n{code}"
        return self._get_completion(prompt, model)

    def compare(self, code1: str, code2: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Compare these two versions of {language.value} code and identify the differences and changes:\n\nVersion 1:\n{code1}\n\nVersion 2:\n{code2}"
        return self._get_completion(prompt, model)

    def complexity_analysis(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Analyze the complexity of the following {language.value} code. Include time and space complexity where applicable:\n\n{code}"
        return self._get_completion(prompt, model)

    def generate_tests(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Generate unit tests for the following {language.value} code:\n\n{code}"
        return self._get_completion(prompt, model)

    def document(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Generate comprehensive documentation for the following {language.value} code:\n\n{code}"
        return self._get_completion(prompt, model)

    def deobfuscate(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Deobfuscate and explain the following {language.value} code:\n\n{code}"
        return self._get_completion(prompt, model)

    def identify_patterns(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Identify and explain common design patterns or architectural patterns in the following {language.value} code:\n\n{code}"
        return self._get_completion(prompt, model)

    def security_audit(self, code: str, language: Language, model: Optional[str] = None) -> str:
        prompt = f"Perform a security audit on the following {language.value} code. Identify potential security vulnerabilities and suggest mitigations:\n\n{code}"
        return self._get_completion(prompt, model)

    def reconstruct_logic(self, assembly_code: str, model: Optional[str] = None) -> str:
        prompt = f"Reconstruct the high-level logic from the following assembly code. Provide a pseudo-code or high-level language equivalent:\n\n{assembly_code}"
        return self._get_completion(prompt, model)

    def save_output(self, output: str, command: str, file: str, output_dir: str = "output", filename: Optional[str] = None):
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

app = typer.Typer()
re_engine = ReverseEngineer()

def common_options(func):
    func = typer.option("--file", help="Path to the file or URL containing the code")(func)
    func = typer.option("--language", default=Language.UNKNOWN, help="Programming language of the code")(func)
    func = typer.option("--model", help="Specific model to use for analysis")(func)
    func = typer.option("--output", help="Name of the output file (optional)")(func)
    return func

@app.command()
@common_options
def analyze(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Analyze the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.analyze(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "analyze", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def identify_issues(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Identify issues in the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.identify_issues(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "identify_issues", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def optimize(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Suggest optimizations for the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.optimize(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "optimize", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def generate_report(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Generate a detailed report for the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.generate_report(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "generate_report", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def extract(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Extract main components from the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.extract(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "extract", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def refactor(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Suggest refactoring for the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.refactor(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "refactor", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def summarize(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Summarize the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.summarize(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "summarize", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def compare(
    file1: str = typer.Option(..., help="Path to the first file or URL containing the code"),
    file2: str = typer.Option(..., help="Path to the second file or URL containing the code"),
    language: Language = Language.UNKNOWN,
    model: Optional[str] = None,
    output: Optional[str] = None
):
    """Compare two code files."""
    code1 = re_engine.read_file(file1)
    code2 = re_engine.read_file(file2)
    result = re_engine.compare(code1, code2, language, model)
    if output:
        saved_path = re_engine.save_output(result, "compare", file1, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def complexity_analysis(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Analyze the complexity of the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.complexity_analysis(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "complexity_analysis", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def generate_tests(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Generate unit tests for the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.generate_tests(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "generate_tests", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def document(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Generate documentation for the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.document(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "document", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def deobfuscate(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Deobfuscate and explain the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.deobfuscate(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "deobfuscate", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def identify_patterns(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Identify design patterns in the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.identify_patterns(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "identify_patterns", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def security_audit(file: str, language: Language, model: Optional[str] = None, output: Optional[str] = None):
    """Perform a security audit on the given code file."""
    code = re_engine.read_file(file)
    result = re_engine.security_audit(code, language, model)
    if output:
        saved_path = re_engine.save_output(result, "security_audit", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

@app.command()
@common_options
def reconstruct_logic(file: str, model: Optional[str] = None, output: Optional[str] = None):
    """Reconstruct high-level logic from assembly code."""
    assembly_code = re_engine.read_file(file)
    result = re_engine.reconstruct_logic(assembly_code, model)
    if output:
        saved_path = re_engine.save_output(result, "reconstruct_logic", file, filename=output)
        typer.echo(f"Output saved to: {saved_path}")
    else:
        typer.echo(result)

if __name__ == "__main__":
    app()

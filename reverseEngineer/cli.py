import shlex
from typing import Optional
import typer
from reverse_engineer import ReverseEngineer, Language, ReverseEngineerError
from utils import read_file, process_command

app = typer.Typer()
re_engine = None

def ensure_initialized(config_path: Optional[str] = None):
    global re_engine
    if re_engine is None:
        typer.echo("Initializing ReverseEngineer with configuration...")
        try:
            re_engine = ReverseEngineer(config_path)
            typer.echo(f"ReverseEngineer initialized with configuration from {config_path or 'default location'}.")
        except ReverseEngineerError as e:
            typer.echo(f"Error initializing ReverseEngineer: {str(e)}", err=True)
            raise typer.Exit(code=1)
        
@app.command()
def init(config_path: str = typer.Option(None, help="Path to the configuration file")):
    """Initialize the ReverseEngineer tool with a configuration file."""
    ensure_initialized(config_path)

@app.callback()
def main(
    ctx: typer.Context,
    config_path: str = typer.Option(None, help="Path to the configuration file")
):
    """Global callback to ensure initialization."""
    ensure_initialized(config_path)

@app.command()
def analyze(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: str = typer.Option(None, help="Specific model to use for analysis"),
    output: str = typer.Option(None, help="Name of the output file (optional)"),
    test_file: Optional[str] = typer.Option(None, help="Optional test file associated with the code")
):
    """Analyze the given code file."""
    _run_command("analyze", file, language, model, output, test_file)

@app.command()
def identify_issues(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: str = typer.Option(None, help="Specific model to use for analysis"),
    output: str = typer.Option(None, help="Name of the output file (optional)")
):
    """Identify issues in the given code file."""
    _run_command("identify_issues", file, language, model, output)

@app.command()
def optimize(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: str = typer.Option(None, help="Specific model to use for analysis"),
    output: str = typer.Option(None, help="Name of the output file (optional)")
):
    """Suggest optimizations for the given code file."""
    _run_command("optimize", file, language, model, output)

@app.command()
def generate_documentation(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: str = typer.Option(None, help="Specific model to use for analysis"),
    output: str = typer.Option(None, help="Name of the output file (optional)")
):
    """Generate documentation for the given code file."""
    _run_command("generate_documentation", file, language, model, output)

@app.command()
def refactor(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: str = typer.Option(None, help="Specific model to use for analysis"),
    output: str = typer.Option(None, help="Name of the output file (optional)"),
    test_file: Optional[str] = typer.Option(None, help="Optional test file associated with the code")
):
    """Suggest refactoring improvements for the given code file."""
    _run_command("refactor", file, language, model, output, test_file)

@app.command()
def explain_algorithm(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: str = typer.Option(None, help="Specific model to use for analysis"),
    output: str = typer.Option(None, help="Name of the output file (optional)")
):
    """Explain the algorithm used in the given code file."""
    _run_command("explain_algorithm", file, language, model, output)

@app.command()
def generate_test_cases(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: str = typer.Option(None, help="Specific model to use for analysis"),
    output: str = typer.Option(None, help="Name of the output file (optional)")
):
    """Generate test cases for the given code file."""
    _run_command("generate_test_cases", file, language, model, output)

@app.command()
def identify_design_patterns(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    language: Language = typer.Option(Language.UNKNOWN, help="Programming language of the code"),
    model: str = typer.Option(None, help="Specific model to use for analysis"),
    output: str = typer.Option(None, help="Name of the output file (optional)")
):
    """Identify design patterns used in the given code file."""
    _run_command("identify_design_patterns", file, language, model, output)

@app.command()
def convert_language(
    file: str = typer.Option(..., help="Path to the file or URL containing the code"),
    from_language: Language = typer.Option(..., help="Source programming language of the code"),
    to_language: Language = typer.Option(..., help="Target programming language for conversion"),
    model: str = typer.Option(None, help="Specific model to use for analysis"),
    output: str = typer.Option(None, help="Name of the output file (optional)")
):
    """Convert the given code file from one programming language to another."""
    if not re_engine:
        typer.echo("Please run 'init' command first to initialize the ReverseEngineer tool.")
        raise typer.Exit(code=1)
    
    try:
        code = read_file(file)
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
    model: str = typer.Option(None, help="Specific model to use for analysis"),
    output: str = typer.Option(None, help="Name of the output file (optional)")
):
    """Perform a security audit on the given code file."""
    _run_command("security_audit", file, language, model, output)

def _run_command(command: str, file: str, language: Language, model: str, output: str, test_file: Optional[str] = None):
    """Helper function to run commands with common logic."""
    
    if not re_engine:
        typer.echo("Please run 'init' command first to initialize the ReverseEngineer tool.")
        raise typer.Exit(code=1)
    
    try:
        # Read the code from the file
        code = read_file(file)

        # Call the corresponding method on re_engine, passing the test file if provided
        if command == "analyze" or command == "refactor":
            # Si le test_file est fourni, passez-le aussi
            if test_file:
                result = getattr(re_engine, command)(file, code, language, model, test_file)
            else:
                result = getattr(re_engine, command)(file, code, language, model)
        else:
            # Pour les autres commandes
            if test_file:
                result = getattr(re_engine, command)(code, language, model, test_file)
            else:
                result = getattr(re_engine, command)(code, language, model)
                
        # If an output file is specified, save the result to the output file
        if output:
            saved_path = re_engine.save_output(result, command, file, filename=output)
            typer.echo(f"Output saved to: {saved_path}")
        else:
            typer.echo(result)
        
        # Enter interactive mode if applicable
        interactive_mode()
    
    except ReverseEngineerError as e:
        typer.echo(f"Error during {command}: {str(e)}", err=True)
        raise typer.Exit(code=1)

def interactive_mode():
    while True:
        command = input("Enter a command (or 'exit' to quit): ").strip()
        if command.lower() in ["exit", "quit"]:
            typer.echo("Exiting...")
            break
        try:
            # Use shlex.split to handle quotes and spaces properly
            args = process_command(command)
            app(prog_name="", args=args)
        except SystemExit as e:
            # Handle Typer's SystemExit so the loop can continue
            if e.code != 0:
                typer.echo(f"Command failed with exit code {e.code}")


if __name__ == "__main__":
    interactive_mode()

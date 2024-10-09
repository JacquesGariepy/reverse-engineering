import ast
import cProfile
from io import StringIO
import os
import pstats
import re
import runpy
import subprocess
import timeit
from typing import List
import coverage
import unittest
import builtins
from line_profiler import LineProfiler

from solid_analyzer import DIPAnalyzer, ISPAnalyzer, LSPAnalyzer, OCPAnalyzer, SOLIDAnalyzerEngine, SRPAnalyzer

class PythonFileLoader:
    def __init__(self, content):
        self.content = content

    def load_file_lines(self) -> list:
        """
        Charge le contenu du fichier sous forme de liste de lignes.
        """
        return self.content.splitlines()

class StaticAnalyzer:

    def __init__(self, file_path, content, test_module=None): 
        self.content = content
        self.loader = PythonFileLoader(content)
        self.test_module = test_module
        self.issues = []
        self.file_path = file_path
        self.MAX_LINE_LENGTH = 80
        self.CHECKS = ["warnings"]
        self.COMPLEXITY_THEMEHOLD = 10 # Maximum cyclomatic complexity threshold
        self.MAX_LINES_PER_FILE = 300  # Maximum number of lines allowed in a file
        self.MAX_FUNCTION_LENGTH = 30  # Maximum number of statements in a function
        self.MAX_CLASS_LENGTH = 150    # Maximum number of statements in a class (across all methods)
        self.MAX_FUNCTION_COUNT = 15  # Maximum number of functions in a file
        self.MAX_CLASS_COUNT = 5     # Maximum number of classes in a file
        self.MAX_FUNC_LENGTH = 50  # Maximum number of lines in a function

    def analyze(self) -> str:
        self.run_checks()

        if not self.issues:
            return "No issues found. The code looks good!"
        else:
            report = f"Static Analysis Report:\n"
            for issue in self.issues:
                report += f"{issue}\n"
            return report

    def run_checks(self):
        
        try:       
            """Exécute toutes les catégories de vérifications."""
            self.check_pyflakes_issues()
            self.check_indentation()
            self.check_code_style()
            self.check_potential_bugs()
            self.check_security()
            self.check_design_principles()
            self.check_maintainability() 
            self.check_complexity()
            self.check_test_coverage()

        except IndentationError as e:
            # Capture des erreurs d'indentation et ajout à la liste des problèmes
            self.issues.append(f"Indentation Error: {str(e)}. Check your code for inconsistent indentation, which can cause issues in Python.")

        except SyntaxError as e:
            # Capture des erreurs de syntaxe dans le code
            self.issues.append(f"Syntax Error: {str(e)} at line {e.lineno}. There may be a missing or misplaced symbol in your code.")

        except AttributeError as e:
            # Capture des erreurs d'attributs
            self.issues.append(f"Attribute Error: {str(e)}. This error may occur if an object is missing an expected attribute or method.")

        except ValueError as e:
            # Capture des erreurs de valeur
            self.issues.append(f"Value Error: {str(e)}. This can happen when an operation receives an argument of the correct type but with an invalid value.")

        except TypeError as e:
            # Capture des erreurs de type
            self.issues.append(f"Type Error: {str(e)}. A function or operation is receiving an argument of the wrong type.")

        except ImportError as e:
            # Capture des erreurs d'importation
            self.issues.append(f"Import Error: {str(e)}. There might be an issue with a missing or incorrect module import.")

        except FileNotFoundError as e:
            # Capture des erreurs de fichiers non trouvés
            self.issues.append(f"File Not Found: {str(e)}. Ensure the file path is correct and the file exists.")

        except KeyError as e:
            # Capture des erreurs de clé non trouvée (par exemple dans un dictionnaire)
            self.issues.append(f"Key Error: {str(e)}. A key used in a dictionary or mapping is missing or incorrect.")

        except IndexError as e:
            # Capture des erreurs d'index hors limites dans des listes ou séquences
            self.issues.append(f"Index Error: {str(e)}. This occurs when trying to access an index that is out of range in a list or sequence.")

        except ZeroDivisionError as e:
            # Capture des erreurs de division par zéro
            self.issues.append(f"Zero Division Error: {str(e)}. This occurs when an attempt is made to divide by zero.")

        except MemoryError as e:
            # Capture des erreurs de mémoire
            self.issues.append(f"Memory Error: {str(e)}. The system ran out of memory when trying to perform an operation.")

        except Exception as e:
            # Capture de toute autre exception non spécifiée
            self.issues.append(f"Unexpected Error: {str(e)}. An unexpected exception occurred.")


    def check_code_style(self):
        """Vérifie le style du code et la conformité à PEP 8."""
        self.check_line_length()
        self.check_docstrings()
        self.check_conformity_to_pep8()
        self.check_functions_length()

    def check_potential_bugs(self):
        """Recherche les bogues potentiels tels que le code mort et les variables non utilisées."""
        self.check_try_except_usage()
        self.check_dead_code()
        self.check_resource_management()
        self.check_concurrency_issues()

    def check_security(self):
        """Recherche les problèmes de sécurité tels que les secrets codés en dur."""
        self.check_secrets_in_code()
        #Bandit: Specifically designed to find common security issues in Python code.
    def check_design_principles(self):
        """Vérifie le respect des principes SOLID."""
        self.check_solid_principles()
        self.check_type_annotations()
        self.check_design_patterns()

    def check_maintainability(self):
        """Vérifie les aspects liés à la maintenabilité du code."""
        self.check_code_duplication()
        self.check_error_handling()
        self.check_logging()
        self.check_dependency_versions()
        self.check_variable_naming_and_builtins()
        self.check_modularity()
        self.check_deprecated_functions()

    def check_indentation(self):
        """Checks for indentation errors in the code."""
        try:
            # Tente de parser le fichier pour détecter les erreurs d'indentation via AST
            content = self.content
            ast.parse(content)
        except IndentationError as e:
            # Capture et stocke les erreurs d'indentation
            self.issues.append(
                f"IndentationError: {str(e)} at line {e.lineno}. "
                "Please ensure the block structure is correctly indented."
            )
        except SyntaxError as e:
            # Capture les erreurs de syntaxe qui peuvent masquer des problèmes d'indentation
            self.issues.append(
                f"SyntaxError: {str(e)} at line {e.lineno}. "
                "There may be a structural issue in the code affecting indentation."
            )

    def check_line_length(self):
        """Vérifie les lignes qui dépassent la longueur maximale autorisée, sauf pour les commentaires et docstrings."""

        in_docstring = False  # Tracks if we're inside a docstring
        lines = self.loader.load_file_lines() 
        for line_num, line in enumerate(lines, 1):
            stripped_line = line.strip()

            # Detect and toggle the start/end of a docstring (""" or ''')
            if stripped_line.startswith(('"""', "'''")):
                # Toggle in_docstring state: enter/exit docstring
                in_docstring = not in_docstring

            # Skip lines that are within a docstring or are comments
            if in_docstring or stripped_line.startswith('#'):
                continue
            
            if len(line) > self.MAX_LINE_LENGTH:
                self.issues.append(
                    f"Line {line_num}: This line exceeds the recommended maximum of {self.MAX_LINE_LENGTH} characters. "
                    f"Lines longer than {self.MAX_LINE_LENGTH} characters are harder to read and maintain."
                )

    def check_docstrings(self):
        """Vérifie les docstrings manquantes dans les fonctions et les classes."""
        try:
            content = self.content
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                    if ast.get_docstring(node) is None:
                        obj_type = "Function" if isinstance(node, ast.FunctionDef) else "Class"
                        self.issues.append(
                            f"{obj_type} '{node.name}' at line {node.lineno} is missing a docstring. "
                            f"Docstrings are important for documenting the purpose and usage of {obj_type.lower()}s, "
                            f"making the code easier to understand and maintain."
                        )
        except IndentationError as e:
            self.issues.append(f"IndentationError: {str(e)}")

    def check_deprecated_functions(self):

        """Checks for the use of deprecated or dangerous functions like eval and exec, and provides alternatives."""
        # Liste des fonctions obsolètes ou dangereuses à éviter avec leurs explications et alternatives
        DEPRECATED_FUNCTIONS = {
            'eval': "Using 'eval' can execute arbitrary code, which is a security risk. Consider using 'ast.literal_eval' if you need to evaluate simple expressions.",
            'exec': "The 'exec' function executes arbitrary code and poses a high security risk. Try to refactor the code to avoid its use.",
            'compile': "The 'compile' function compiles source code into bytecode, but it allows the execution of dynamic code, which can be dangerous. Avoid executing dynamic code where possible.",
            'globals': "The 'globals()' function gives access to the global symbol table, which can lead to unpredictable behavior. Avoid modifying global variables dynamically.",
            'locals': "The 'locals()' function allows access to the local variable scope, which can lead to unexpected behavior. Avoid its use for modifying local variables dynamically.",
            'open': "Using 'open()' without proper validation of file paths can lead to directory traversal attacks. Ensure proper validation of user inputs for file paths.",
            'os.system': "The 'os.system()' function allows the execution of shell commands, which can be exploited for command injection attacks. Use 'subprocess.run()' with argument lists instead.",
            'subprocess.Popen': "When using 'subprocess.Popen()', avoid using 'shell=True', which opens the door to shell injection attacks. Use argument lists instead for better security.",
            'pickle.loads': "The 'pickle.loads()' function can deserialize arbitrary code, leading to remote code execution attacks. Use safer serialization formats like JSON.",
            'hashlib.md5': "The 'MD5' algorithm is considered cryptographically broken and unsuitable for further use. Use 'hashlib.sha256()' or a more secure algorithm.",
            'hashlib.sha1': "The 'SHA-1' algorithm is considered insecure due to vulnerabilities. Use 'hashlib.sha256()' or a stronger algorithm like 'SHA-3'.",
            'random': "The 'random' module is not suitable for cryptographic purposes. Use the 'secrets' module for generating cryptographically secure random numbers.",
            'input': "In Python 2.x, 'input()' evaluates user input as Python code, which is unsafe. Use 'raw_input()' in Python 2.x, or 'input()' in Python 3.x, which is safe."
        }
        
        content = self.content
        tree = ast.parse(content)

        for node in ast.walk(tree):
            # Vérifier si une fonction obsolète est utilisée
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in DEPRECATED_FUNCTIONS:
                    # Ajouter l'explication du problème et l'alternative à self.issues
                    self.issues.append(
                        f"Line {node.lineno}: Usage of deprecated function '{node.func.id}'. "
                        f"{DEPRECATED_FUNCTIONS[node.func.id]}"
                    )

            # Vérification des docstrings pour mention de dépréciation
            elif isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                docstring = ast.get_docstring(node)
                if docstring and any(keyword in docstring.lower() for keyword in ["deprecated", "will be removed", "obsoleted", "outdated"]):
                    self.issues.append(
                        f"{'Function' if isinstance(node, ast.FunctionDef) else 'Class'} '{node.name}' on line {node.lineno} is marked as deprecated in its documentation."
                    )

    def check_complexity(self):
        """Uses flake8 with mccabe to check the cyclomatic complexity of the code and report only if it exceeds the threshold."""
        
        try:
            # Exécuter flake8 avec la règle de complexité et capturer la sortie
            result = subprocess.run(
                ['flake8', '--max-complexity', str(self.COMPLEXITY_THEMEHOLD), self.file_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            # Si flake8 retourne des résultats
            if result.stdout:
                # Traiter la sortie ligne par ligne et n'ajouter que si la complexité dépasse le seuil
                for line in result.stdout.splitlines():
                    # Flake8 retourne les lignes où la complexité dépasse le seuil
                    if "C901" in line:
                        self.issues.append(line)
            else:
                self.issues.append("No functions with complexity exceeding the threshold.")

        except Exception as e:
            self.issues.append(f"Error occurred while calculating cyclomatic complexity: {str(e)}")

    def check_pyflakes_issues(self):
        """Analyzes the code for all logic or import errors using pyflakes and captures all issues."""
        
        try:
            # Exécuter pyflakes sur le fichier et capturer la sortie
            result = subprocess.run(
                ['pyflakes', self.file_path],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            
            # Vérifier si pyflakes a retourné des résultats
            if result.stdout:
                # Ajouter chaque ligne de sortie directement à self.issues
                self.issues.extend(result.stdout.splitlines())
        
            return self.issues
        
        except Exception as e:
            return [f"Error occurred while checking pyflakes issues: {str(e)}"]
                
    def check_try_except_usage(self, max_try_except_threshold=3):
        """Check if a method or function exceeds the maximum number of allowed try-except blocks."""
        try:
            content = self.content
            tree = ast.parse(content)

            def count_try_except_in_node(node):
                """Count the number of try-except blocks in the given function or method."""
                try_except_count = 0

                # Walk through the AST nodes of the function or method to count try-except blocks
                for child in ast.walk(node):
                    if isinstance(child, ast.Try):
                        try_except_count += 1

                return try_except_count

            # Traverse the AST to find function definitions and class methods
            for node in ast.walk(tree):
                # Handle both functions and methods (including __init__)
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    try_except_count = count_try_except_in_node(node)

                    # If the count exceeds the max threshold, report an issue
                    if try_except_count > max_try_except_threshold:
                        self.issues.append(
                            f"Function or method '{node.name}' at line {node.lineno} contains too many try-except blocks "
                            f"({try_except_count}). Consider refactoring the function."
                        )
        except Exception as e:
            self.issues.append(f"Error occurred during try-except block check: {str(e)}")

    def check_dead_code(self):
        """Identifies dead code (code that is never executed)."""
        try:
            content = self.content
            tree = ast.parse(content)

            def detect_unreachable_code_after_statements(node):
                """Detect code that is unreachable after control-flow altering statements."""
                unreachable = False

                for child in node.body:
                    if unreachable:
                        self.issues.append(
                            f"Line {child.lineno}: Detect unreachable code following a control flow statement. Given a piece of code, identify any code that will never be executed due to an earlier return, break, continue, or other control flow changes. Highlight the unreachable section and explain the specific control flow that causes it to be skipped"
                        )
                    if isinstance(child, (ast.Return, ast.Break, ast.Continue, ast.Raise)):
                        unreachable = True  # Mark the code following this as unreachable

            def detect_constant_conditions(node):
                """Detect constant conditions in if or while statements."""
                if isinstance(node.test, ast.Constant):
                    if node.test.value is False:
                        self.issues.append(
                            f"Line {node.lineno}: Identify code where a condition always evaluates to false, rendering a block of code dead. Analyze logical errors that lead to impossible conditions, and flag the unreachable block."
                        )
                    elif node.test.value is True:
                        self.issues.append(
                            f"Line {node.lineno}: Detect a while loop condition that can never be true, leading to code that will never run. Explain why the loop is non-executable and what conditions prevent it from running."
                        )

            # Traverse the AST to find dead code patterns
            for node in ast.walk(tree):
                # Check for unreachable code after return, break, continue, or raise
                if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                    detect_unreachable_code_after_statements(node)
                elif isinstance(node, ast.If):
                    detect_constant_conditions(node)
                elif isinstance(node, ast.While):
                    detect_constant_conditions(node)
                    # Check if the while loop will never execute (e.g., while False)
                    if isinstance(node.test, ast.Constant) and node.test.value is False:
                        self.issues.append(
                            f"Line {node.lineno}: Dead code detected - while loop will never execute."
                        )
        except Exception as e:
            self.issues.append(f"Error occurred during dead code check: {str(e)}")

    def check_modularity(self):
        """Checks whether the code is well-structured into logical modules and functions."""

        # Define threshold values for testing modularity
        try:
            MAX_LINES_PER_FILE = self.MAX_LINES_PER_FILE
            MAX_FUNCTION_LENGTH = self.MAX_FUNCTION_LENGTH
            MAX_CLASS_LENGTH = self.MAX_CLASS_LENGTH
            MAX_FUNCTION_COUNT = self.MAX_FUNCTION_COUNT
            MAX_CLASS_COUNT = self.MAX_CLASS_COUNT

            content = self.content
            tree = ast.parse(content)
            lines = self.loader.load_file_lines()
            # Check for large files based on line count
            if len(lines) > MAX_LINES_PER_FILE:
                self.issues.append(
                    f"Contains too many lines ({len(lines)}). Consider splitting into smaller modules."
                )

            function_count = 0
            class_count = 0
            large_functions = []
            large_classes = []

            # Traverse the AST nodes to analyze function and class sizes
            for node in ast.walk(tree):
                # Count function definitions and check their length
                if isinstance(node, ast.FunctionDef):
                    function_count += 1
                    function_length = len(node.body)
                    if function_length > MAX_FUNCTION_LENGTH:
                        large_functions.append((node.name, function_length, node.lineno))

                # Count class definitions and check their length
                if isinstance(node, ast.ClassDef):
                    class_count += 1
                    class_length = sum(len(n.body) for n in node.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)))
                    if class_length > MAX_CLASS_LENGTH:
                        large_classes.append((node.name, class_length, node.lineno))

            # Report if there are too many functions or classes in the file
            if function_count > MAX_FUNCTION_COUNT:
                self.issues.append(
                    f"Contains too many functions ({function_count}). Consider refactoring."
                )

            if class_count > MAX_CLASS_COUNT:
                self.issues.append(
                    f"Contains too many classes ({class_count}). Consider refactoring."
                )

            # Report large functions
            for func_name, func_length, lineno in large_functions:
                self.issues.append(
                    f"Function '{func_name}' at line {lineno} is too large ({func_length} statements). "
                    "Consider refactoring into smaller functions."
                )

            # Report large classes
            for class_name, class_length, lineno in large_classes:
                self.issues.append(
                    f"Class '{class_name}' at line {lineno} is too large ({class_length} total statements in methods). "
                    "Consider splitting it into smaller classes or modules."
                )

        except Exception as e:
            self.issues.append(f"Error occurred during modularity check: {str(e)}")

    def check_variable_naming_and_builtins(self):
        """Checks variable, function names for PEP 8 violations and flags dangerous or deprecated built-in usage."""
        try:
            content = self.content
            tree = ast.parse(content)

            snake_case_pattern = r'^[a-z_][a-z0-9_]*$'  # Snake case for variables and functions
            pascal_case_pattern = r'^[A-Z][a-zA-Z0-9]*$'  # Pascal case for class names
            upper_case_pattern = r'^[A-Z_][A-Z0-9_]*$'  # Upper case for constants
            
            builtins_names = dir(builtins)  # Built-in Python names to check for shadowing
            dangerous_builtins = ['eval', 'exec']  # Potentially dangerous built-ins
            deprecated_builtins = ['apply']  # Deprecated built-ins

            for node in ast.walk(tree):
                # Check variable and function names (should be in snake_case)
                if isinstance(node, ast.Name):
                    # Skip checking variables inside type annotations (as in function signatures)
                    if isinstance(node.ctx, ast.Store) and not isinstance(node, ast.arg):
                        if not re.match(snake_case_pattern, node.id):
                            self.issues.append(
                                f"Variable '{node.id}' does not follow snake_case naming convention."
                            )
                        # Check if variable shadows a built-in name
                        elif node.id in builtins_names:
                            self.issues.append(
                                f"Variable '{node.id}' shadows a Python built-in name. Consider renaming."
                            )

                # Check function names (should be in snake_case)
                if isinstance(node, ast.FunctionDef):
                    if not re.match(snake_case_pattern, node.name):
                        self.issues.append(
                            f"Function '{node.name}' does not follow snake_case naming convention."
                        )

                    # Check function parameters for snake_case
                    for arg in node.args.args:
                        if not re.match(snake_case_pattern, arg.arg):
                            self.issues.append(
                                f"Function argument '{arg.arg}' in function '{node.name}' does not follow snake_case."
                            )

                # Check class names (should be in PascalCase)
                if isinstance(node, ast.ClassDef):
                    if not re.match(pascal_case_pattern, node.name):
                        self.issues.append(
                            f"Class '{node.name}' does not follow PascalCase naming convention."
                        )

                # Check constants (typically defined in uppercase)
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id.isupper():
                            if not re.match(upper_case_pattern, target.id):
                                self.issues.append(
                                    f"Constant '{target.id}' should follow UPPER_CASE naming convention."
                                )

                # Check for dangerous built-in usage (like eval, exec)
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in dangerous_builtins:
                        self.issues.append(
                            f"Potentially dangerous use of built-in function '{node.func.id}' at line {node.lineno}. "
                            "Consider avoiding its use or review its necessity."
                        )

                    # Check for deprecated built-ins
                    if node.func.id in deprecated_builtins:
                        self.issues.append(
                            f"Usage of deprecated built-in function '{node.func.id}' at line {node.lineno}. "
                            "Consider using a modern alternative."
                        )

                # Detect misuse of __builtins__
                if isinstance(node, ast.Attribute) and node.attr == '__builtins__':
                    self.issues.append(
                        f"Direct use of '__builtins__' detected at line {node.lineno}. "
                        "Avoid modifying '__builtins__' as it can affect global behavior."
                    )

        except SyntaxError as e:
            self.issues.append(f"SyntaxError in file: {str(e)} at line {e.lineno}")
        except Exception as e:
            self.issues.append(f"Error occurred during naming and built-in usage check: {str(e)}")

    # TODO : To be reviewed and updated
    def check_resource_management(self):
        """Checks for proper resource management, ensuring files, sockets, and other resources are properly closed."""
        try:
            content = self.content
            tree = ast.parse(content)

            # Dictionary of resources and their expected closing method
            resource_types = {
                'open': 'close',                # Files
                'socket': 'close',              # Sockets
                'connect': 'close',             # Database connections (e.g., sqlite3.connect())
                'requests.get': 'close',        # HTTP requests (requests library)
                'NamedTemporaryFile': 'close',  # Temporary files (tempfile library)
                'Thread': 'join',               # Threads (threading library)
            }

            # Walk through the AST to find resource-related issues
            for node in ast.walk(tree):
                if isinstance(node, ast.With):
                    # Skip 'with' statements since they handle resources correctly
                    context_expr = node.items[0].context_expr
                    if isinstance(context_expr, ast.Call) and isinstance(context_expr.func, (ast.Name, ast.Attribute)):
                        resource = self.get_resource_name(context_expr.func)
                        if resource in resource_types:
                            # Resource managed by 'with', skip as it's safe
                            continue

                # Check for resource-opening calls like 'open()', 'socket()', 'connect()', etc.
                elif isinstance(node, ast.Call):
                    resource = None
                    # Check if the function is a direct resource, e.g., 'open()' or an attribute like 'requests.get'
                    if isinstance(node.func, (ast.Name, ast.Attribute)):
                        resource = self.get_resource_name(node.func)
                    
                    if resource in resource_types:
                        # Check if the resource is properly closed within the same function
                        parent_function = self.get_parent_function(node, tree)
                        resource_closed = False
                        if parent_function:
                            for n in ast.walk(parent_function):
                                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute):
                                    # Check if the close/join method is called
                                    if n.func.attr == resource_types[resource]:
                                        resource_closed = True
                                        break
                        
                        if not resource_closed:
                            self.issues.append(
                                f"Line {node.lineno}: Resource '{resource}' opened but not properly closed. "
                                f"Ensure '{resource_types[resource]}' is called to avoid leaks."
                            )

        except SyntaxError as e:
            self.issues.append(f"SyntaxError in file: {str(e)} at line {e.lineno}")
        except Exception as e:
            self.issues.append(f"Error occurred during resource management check: {str(e)}")


    def get_parent_function(self, node, tree):
        """Helper function to get the parent function of a node."""
        for ancestor in ast.walk(tree):
            if isinstance(ancestor, ast.FunctionDef):
                for child in ast.walk(ancestor):
                    if node is child:
                        return ancestor
        return None

    def get_resource_name(self, func_node):
        """Helper function to retrieve the resource name from an AST function node."""
        if isinstance(func_node, ast.Name):
            return func_node.id
        elif isinstance(func_node, ast.Attribute):
            if isinstance(func_node.value, ast.Name):
                return f"{func_node.value.id}.{func_node.attr}"  # e.g., 'requests.get'
            # Handles cases like 'socket.socket'
            elif isinstance(func_node.value, ast.Attribute):
                return f"{func_node.value.attr}.{func_node.attr}"  
        return None


    def check_conformity_to_pep8(self, ignore=None, verbose=False):
        """
        Vérifie la conformité aux normes PEP 8 en utilisant pycodestyle et ajoute les problèmes à self.issues.
        
        Args:
            max_line_length (int): Longueur maximale autorisée des lignes (par défaut 79 caractères selon PEP 8).
            ignore (list): Liste des codes d'erreur PEP 8 à ignorer (par exemple ['E501'] pour ignorer les lignes longues).
            verbose (bool): Si True, fournir des détails sur les violations de PEP 8.
        """
        import pycodestyle
        try:
            # Crée un rapport personnalisé pour capturer les erreurs
            class CustomReport(pycodestyle.BaseReport):
                def __init__(self, options):
                    super().__init__(options)
                    self.errors = []

                def error(self, line_number, offset, text, check):
                    """Capture les erreurs et les ajoute à self.errors sous forme lisible."""
                    code = text.split()[0]
                    error_message = f"Line {line_number}, Column {offset + 1}: {code} {text[len(code)+1:]}"
                    self.errors.append(error_message)
                    return super().error(line_number, offset, text, check)

            # Configurer le style guide avec le rapport personnalisé
            style_guide = pycodestyle.StyleGuide(
                quiet=not verbose,
                max_line_length=self.MAX_LINES_PER_FILE,
                reporter=CustomReport  # Utilise le rapport personnalisé
            )

            if ignore:
                style_guide.options.ignore = ignore

            # Exécuter la vérification sur le fichier
            report = style_guide.check_files([self.file_path])

            # Ajout des erreurs au lieu du simple nombre
            if report.total_errors > 0:
                self.issues.append(f"{report.total_errors} PEP 8 violations found.")
                self.issues.extend(report.errors)  # Ajoute chaque erreur spécifique à self.issues
            else:
                self.issues.append("No PEP 8 violations found.")

        except ImportError:
            self.issues.append("Pycodestyle package is required for PEP 8 compliance check.")
        
        except Exception as e:
            self.issues.append(f"Error occurred during PEP 8 check: {str(e)}")

    def check_functions_length(self):
        """Vérifie les fonctions qui sont trop longues, suggérant une refactorisation possible."""

        content = self.content
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_length = len(node.body)
                if func_length > self.MAX_FUNC_LENGTH:
                    self.issues.append(
                        f"Function '{node.name}' at line {node.lineno} is too long ({func_length} lines). Consider refactoring."
                    )

    def check_dependency_versions(self):
        """Vérifie les dépendances obsolètes en tenant compte des imports du fichier."""
        try:
            # Analyse des imports dans le fichier
            content = self.content
            tree = ast.parse(content)

            imported_modules = set()
            # Parcourt l'arbre syntaxique pour trouver les modules importés
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        # Récupère le nom du module importé (ex: 'os' ou 'numpy')
                        imported_modules.add(alias.name.split('.')[0])
                elif isinstance(node, ast.ImportFrom):
                    # Récupère le nom du module parent (ex: 'from numpy import ...')
                    imported_modules.add(node.module.split('.')[0])

            # Vérifie les dépendances obsolètes avec pip
            result = subprocess.run(['pip', 'list', '--outdated', '--format=freeze'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    text=True)

            outdated_dependencies = []
            if result.stdout:
                # Analyse la liste des paquets obsolètes
                for line in result.stdout.splitlines():
                    package_name = line.split('==')[0]
                    # Vérifie si le package obsolète est utilisé dans le fichier
                    if package_name in imported_modules:
                        outdated_dependencies.append(line)

            if outdated_dependencies:
                # Ajoute les dépendances obsolètes à la liste des problèmes
                formatted_deps = "\n".join(outdated_dependencies)
                self.issues.append(f"Outdated dependencies found:\n{formatted_deps}")
                
        except FileNotFoundError:
            self.issues.append("Dependency version check skipped: pip not accessible.")
        except Exception as e:
            self.issues.append(f"An error occurred during dependency check: {str(e)}")

    def run_tests(self):
        """Exécute les tests unitaires et retourne les résultats."""
        test_loader = unittest.TestLoader()
        suite = test_loader.loadTestsFromModule(self.test_module)

        runner = unittest.TextTestRunner()
        result = runner.run(suite)
        
        if not result.wasSuccessful():
            self.issues.append("Some tests failed.")
        
        return result

    def check_test_coverage(self):
        """Vérifie la couverture des tests par rapport au code source."""
        try:
            # Initialiser la couverture
            cov = coverage.Coverage()
            cov.start()

            # Exécuter les tests unitaires
            test_results = self.run_tests()

            cov.stop()
            cov.save()

            # Générer un rapport de couverture
            coverage_report = cov.report()

            # Vérifier la couverture minimale
            if coverage_report < 80.0:  # Exemple de seuil pour la couverture minimale
                self.issues.append(
                    f"Test coverage is below threshold: {coverage_report}% coverage."
                )
            else:
                self.issues.append(f"Test coverage: {coverage_report}%")

        except Exception as e:
            self.issues.append(f"Test coverage check failed: {str(e)}")

    def check_concurrency_issues(self):
        """Identifies concurrency issues such as improper usage of locks and access to shared resources."""
        try:
            content = self.content
            tree = ast.parse(content)

            shared_resource_access = []
            
            # Walk through the AST to find potential concurrency issues
            for node in ast.walk(tree):
                # Check if ThreadPoolExecutor or threading.Thread is used, implying potential concurrency
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['submit', 'map']:  # ThreadPoolExecutor methods
                        self.issues.append(
                            f"Line {node.lineno}: Potential multithreading detected with ThreadPoolExecutor. Check for shared resources."
                        )

                # Check for threading.Lock acquire/release usage
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['acquire', 'release']:
                        self.issues.append(
                            f"Line {node.lineno}: Possible improper use of locks. Ensure proper usage to avoid deadlocks."
                        )

                # Detect shared resource access in potential multithreading contexts
                if isinstance(node, ast.Assign):
                    # Check if shared resources (lists, dicts) are being assigned to in the presence of multithreading
                    if isinstance(node.targets[0], (ast.Subscript, ast.Attribute)):
                        shared_resource_access.append(f"Line {node.lineno}: Shared resource access detected.")
                        
            # Only report shared resource access if multithreading is detected
            if shared_resource_access and any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr in ['submit', 'map'] for n in ast.walk(tree)):
                self.issues.extend(shared_resource_access)

        except Exception as e:
            self.issues.append(f"Error occurred during concurrency check: {str(e)}")


    import ast

    def check_solid_principles(self):
        """
        Fonction principale pour exécuter l'analyse statique d'un fichier Python
        avec les règles SOLID. Respecte le DIP en injectant les analyseurs dans le moteur.
        """
        # Charger le fichier Python
        content = self.content

        # Initialiser le moteur avec les différents analyseurs SOLID
        solid_engine = SOLIDAnalyzerEngine([
            SRPAnalyzer(),
            OCPAnalyzer(),
            LSPAnalyzer(),
            ISPAnalyzer(),
            DIPAnalyzer()
        ])

        # Exécuter l'analyse avec le moteur et ajouter les résultats à self.issues
        solid_issues = solid_engine.analyze_code(content)
        self.issues.extend(solid_issues)  # Ajouter les problèmes détectés par le moteur SOLID

        # Analyse manuelle basée sur l'AST pour compléter l'analyse
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Vérification SRP : trop de méthodes dans une classe
                if len([n for n in node.body if isinstance(n, ast.FunctionDef)]) > 10:
                    self.issues.append(
                        f"Class '{node.name}' at line {node.lineno} might violate the Single Responsibility Principle by having too many methods."
                    )

                # Vérification OCP : utilisation excessive de méthodes protégées
                if any(isinstance(n, ast.FunctionDef) and n.name.startswith('_') for n in node.body):
                    self.issues.append(
                        f"Class '{node.name}' at line {node.lineno} might be using too many protected methods. "
                        f"Consider if the class can be extended without modification."
                    )

    
    def check_type_annotations(self):
        """Vérifie les annotations de type manquantes dans les définitions de fonctions."""
        content = self.content
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                if not node.returns or not all(arg.annotation is not None for arg in node.args.args):
                    self.issues.append(
                        f"Function '{node.name}' at line {node.lineno} is missing type annotations."
                    )

    def check_design_patterns(self):
        """Identifie les modèles de conception utilisés dans le code."""
        content = self.content
        tree = ast.parse(content)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and any(isinstance(n, ast.FunctionDef) and n.name == '__init__' for n in node.body):
                if any(isinstance(stmt, ast.Assign) for stmt in node.body):
                    self.issues.append(
                        f"Class '{node.name}' at line {node.lineno} seems to implement the Singleton pattern."
                    )

    def check_secrets_in_code(self):
        """Vérifie les clés API ou les secrets codés en dur dans le code source."""
        SECRET_PATTERNS = [
            r'AKIA[0-9A-Z]{16}',  # Modèle de clé d'accès AWS
            r'AIza[0-9A-Za-z-_]{35}',  # Modèle de clé API Google
            r'[A-Za-z0-9_]{20,}',  # Modèles génériques de type jeton long
        ]
        lines = self.loader.load_file_lines()
        for line_num, line in enumerate(lines, 1):
            for pattern in SECRET_PATTERNS:
                if re.search(pattern, line):
                    self.issues.append(f"Line {line_num}: Potential secret found in code.")
                    
    def check_code_duplication(self):
        """Identifies duplicated blocks of code while ignoring whitespaces, comments, and irrelevant lines."""
        
        def normalize_line(line):
            """Normalize a line by removing comments and extra whitespace."""
            # Remove comments (anything after a #)
            line_without_comments = re.sub(r'#.*', '', line)
            # Strip leading and trailing whitespace and collapse multiple spaces into one
            normalized = re.sub(r'\s+', ' ', line_without_comments.strip())
            return normalized

        lines = self.loader.load_file_lines()
        seen_blocks = set()
        block_size = 3  # Number of consecutive lines to consider a block
        block = []

        for i, line in enumerate(lines):
            normalized_line = normalize_line(line)

            # Skip empty or irrelevant lines
            if not normalized_line:
                continue

            block.append(normalized_line)

            # Once we have a block of the desired size, check for duplication
            if len(block) == block_size:
                block_tuple = tuple(block)

                if block_tuple in seen_blocks:
                    self.issues.append(
                        f"Lines {i - block_size + 2}-{i+1}: Possible code duplication detected."
                    )
                else:
                    seen_blocks.add(block_tuple)

                # Slide the window: remove the first line and continue with the next
                block.pop(0)

    def check_error_handling(self):
        """Analyse la gestion des erreurs dans le fichier."""
        content = self.content
        tree = ast.parse(content)

        for node in ast.walk(tree):
            if isinstance(node, ast.Try):
                # Vérifier chaque clause 'except'
                for handler in node.handlers:
                    if handler.type is None:
                        self.issues.append(
                            f"Line {handler.lineno}: Bare except clause detected. It is recommended to catch specific exceptions."
                        )
                    elif isinstance(handler.type, ast.Name) and handler.type.id == "Exception":
                        self.issues.append(
                            f"Line {handler.lineno}: Too general exception handling. Consider specifying exception types."
                        )
                    # Vérification supplémentaire : s'assurer qu'une action est effectuée dans le bloc except
                    if not any(isinstance(h, ast.Expr) for h in handler.body):
                        self.issues.append(
                            f"Line {handler.lineno}: No action taken in the exception handler. Consider adding logging, re-raising, or other error handling."
                        )

                    # Vérifier la présence de la journalisation ou d'une autre action dans les clauses except
                    has_logging = False
                    for stmt in handler.body:
                        if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                            if isinstance(stmt.value.func, ast.Attribute):
                                if stmt.value.func.attr in ["debug", "info", "warning", "error", "critical"]:
                                    has_logging = True
                    if not has_logging:
                        self.issues.append(
                            f"Line {handler.lineno}: No logging or specific error handling found in the exception block."
                        )

    def check_logging(self):
        """Vérifie la présence et la qualité des instructions de journalisation."""
        content = self.content
        tree = ast.parse(content)

        has_logging_import = False
        for node in ast.walk(tree):
            # Vérifier si le module logging est importé
            if isinstance(node, ast.ImportFrom):
                if node.module == "logging":
                    has_logging_import = True

            # Vérifier l'utilisation des fonctions de journalisation
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                if node.func.attr in ["debug", "info", "warning", "error", "critical"]:
                    # Check if the logging statement has a message and if the message is a string
                    if len(node.args) == 0 or not isinstance(node.args[0], ast.Constant) or not isinstance(node.args[0].value, str):
                        self.issues.append(
                            f"Line {node.lineno}: Logging statement has no message or the message is not a string."
                        )
                    # Check if the message is sufficiently descriptive (minimum length)
                    elif len(node.args[0].value) < 10:
                        self.issues.append(
                            f"Line {node.lineno}: Logging message too short. Consider providing a more detailed message."
                        )

        if not has_logging_import:
            self.issues.append(
                "No logging module imported. Consider adding 'import logging' at the top of the file."
            )

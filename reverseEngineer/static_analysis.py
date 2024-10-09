import ast
import cProfile
from io import StringIO
import os
import pstats
import re
import subprocess
import timeit
from typing import List
import coverage
import unittest

class StaticAnalyzer:

    def __init__(self, file_path, test_module=None, checks=["warnings"], complexity_threshold=1):
        self.file_path = file_path
        self.test_module = test_module
        self.issues = []
        self.MAX_LINE_LENGTH = 80
        self.checks = checks
        self.complexity_threshold = complexity_threshold

    def analyze(self) -> str:
        self.run_checks()

        if not self.issues:
            return "No issues found. The code looks good!"
        else:
            report = f"Static Analysis Report for {self.file_path}:\n"
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
            self.check_performance()
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
        self.check_unused_imports()
        self.check_unused_variables()
        self.check_try_except_usage()
        self.check_dead_code()
        self.check_resource_management()
        self.check_concurrency_issues()

    def check_security(self):
        """Recherche les problèmes de sécurité tels que les secrets codés en dur."""
        self.check_secrets_in_code()

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
        self.check_variable_naming()
        self.check_complexity()
        self.check_modularity()
        self.check_deprecated_functions()

    def check_performance(self):
        """Vérifie les problèmes de performance potentiels."""
        self.check_performance_issues()

    def check_indentation(self):
        """Checks for indentation errors in the code."""
        try:
            # Tente de parser le fichier pour détecter les erreurs d'indentation via AST
            with open(self.file_path, 'r') as file:
                file_content = file.read()
            ast.parse(file_content)
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
        with open(self.file_path, 'r') as file:
            lines = file.readlines()
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
        with open(self.file_path, 'r') as file:
            try:
                tree = ast.parse(file.read())
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
        
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())

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
                ['flake8', '--max-complexity', str(self.complexity_threshold), self.file_path],
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
            else:
                self.issues.append("No pyflakes issues detected.")

            return self.issues
        
        except Exception as e:
            return [f"Error occurred while checking pyflakes issues: {str(e)}"]

    def check_unused_imports(self):
        """Vérifie les importations non utilisées dans le code."""
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())
            imported_names = set()
            used_names = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imported_names.add(alias.name)
                elif isinstance(node, ast.Name):
                    used_names.add(node.id)

            for name in imported_names:
                if name not in used_names:
                    self.issues.append(f"Unused import '{name}' found in the code.")

    def check_unused_variables(self):
        """Vérifie les variables qui sont assignées mais jamais utilisées."""
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())

        def check_scope(node):
            assigned_vars = set()
            used_vars = set()
            for child in ast.walk(node):
                if isinstance(child, ast.Assign):
                    for target in child.targets:
                        if isinstance(target, ast.Name):
                            assigned_vars.add(target.id)
                elif isinstance(child, ast.Name):
                    used_vars.add(child.id)
            for var in assigned_vars:
                if var not in used_vars:
                    self.issues.append(f"Variable '{var}' is assigned but never used.")

        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                check_scope(node)

    def check_try_except_usage(self):
        """Vérifie si les blocs try-except sont trop généraux."""
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Try):
                    if any(isinstance(handler.type, ast.Name) and handler.type.id == 'Exception' for handler in node.handlers):
                        self.issues.append(
                            f"Line {node.lineno}: Too general exception handling. Consider specifying exception types."
                        )

    def check_dead_code(self):
        """Identifie le code qui n'est jamais exécuté (code mort)."""
        # (Implémentation plus avancée avec l'analyse du flux de contrôle à ajouter ici)
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.If):
                    if isinstance(node.test, ast.Constant) and not node.test.value:
                        self.issues.append(
                            f"Line {node.lineno}: Dead code detected - condition will always be false."
                        )

    def check_modularity(self):
        """Vérifie si le code est bien structuré en modules logiques."""
        # Exemple de critère : Nombre de lignes dans un fichier/module
        with open(self.file_path, 'r') as file:
            lines = file.readlines()

        if len(lines) > 500:  # Seuil d'exemple
            self.issues.append(
                f"The file {self.file_path} has too many lines ({len(lines)}). Consider splitting into smaller modules."
            )

    def check_variable_naming(self):
        """Vérifie les conventions de nommage des variables (PEP 8)."""
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Name) and not re.match(r'^[a-z_][a-z0-9_]*$', node.id):
                    self.issues.append(
                        f"Variable '{node.id}' does not follow snake_case naming convention."
                    )

    def check_resource_management(self):
        """Vérifie la gestion correcte des ressources, par exemple les opérations de fermeture de fichiers."""
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.With):
                    # Si nous utilisons 'with', les ressources sont généralement gérées correctement.
                    continue
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id == 'open':
                        # Vérifier si le fichier est fermé dans la même fonction
                        if not any(isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == 'close' for n in ast.walk(node)):  
                            self.issues.append(
                                f"Line {node.lineno}: Potential resource leak detected - ensure file is properly closed."
                            )

    def check_conformity_to_pep8(self):
        try:
            import pycodestyle
            style_guide = pycodestyle.StyleGuide(quiet=True)
            report = style_guide.check_files([self.file_path])

            if report.total_errors > 0:
                self.issues.append(
                    f"{report.total_errors} PEP8 violations found. Consider fixing style issues."
                )
        except ImportError:
            self.issues.append("Pycodestyle package is required for PEP8 compliance check.")

    def check_functions_length(self):
        """Vérifie les fonctions qui sont trop longues, suggérant une refactorisation possible."""
        MAX_FUNC_LENGTH = 50  # Exemple de seuil en lignes de code
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    func_length = len(node.body)
                    if func_length > MAX_FUNC_LENGTH:
                        self.issues.append(
                            f"Function '{node.name}' at line {node.lineno} is too long ({func_length} lines). Consider refactoring."
                        )

    def check_dependency_versions(self):
        """Vérifie les dépendances obsolètes en tenant compte des imports du fichier."""
        try:
            # Analyse des imports dans le fichier
            with open(self.file_path, 'r') as file:
                tree = ast.parse(file.read())

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

    def check_performance_issues(self):
        """Checks for inefficient loops or data structures, and performs profiling using cProfile, timeit, and line_profiler."""
        
        # Analyse statique des boucles et des structures de données
        try:
            with open(self.file_path, 'r') as file:
                tree = ast.parse(file.read())
                code = file.read()  # Charger le code source pour exécution et profilage

            for node in ast.walk(tree):
                if isinstance(node, ast.For):
                    # Vérification si la boucle itère sur une liste (structure inefficace)
                    if isinstance(node.iter, ast.List):
                        self.issues.append(
                            f"Line {node.lineno}: Iterating directly over a list. "
                            "Consider using a set for faster lookups, as sets provide O(1) lookup time while lists have O(n)."
                        )

                elif isinstance(node, ast.While):
                    # Détection des boucles while, avec une mise en garde sur leur efficacité
                    self.issues.append(
                        f"Line {node.lineno}: Detected a 'while' loop. Ensure it is properly optimized and will not run indefinitely."
                    )

            # Si des boucles sont détectées, effectuer un profilage détaillé
            self.run_performance_profiling(code)

        except SyntaxError as e:
            self.issues.append(f"SyntaxError in the code at line {e.lineno}: {str(e)}")
        except Exception as e:
            self.issues.append(f"An unexpected error occurred during performance check: {str(e)}")


    def run_performance_profiling(self, code):
        """Performs performance profiling using cProfile, timeit, and provides hooks for line_profiler."""
        
        # Profiling avec cProfile
        pr = cProfile.Profile()
        pr.enable()

        # Exécuter dynamiquement le code du fichier source
        try:
            exec(code, globals())  # Exécute dynamiquement le code fourni
        except Exception as e:
            self.issues.append(f"Profiling failed: {str(e)}")
            return

        pr.disable()
        
        # Stockage du résultat du profilage dans un StringIO
        s = StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()

        # Ajout des résultats du profilage cProfile aux issues
        self.issues.append(f"Performance profiling (cProfile) results:\n{s.getvalue()}")

        # Utilisation de timeit pour mesurer une portion critique de code
        try:
            # Chronométrer l'exécution globale du fichier source
            exec_time = timeit.timeit(lambda: exec(code, globals()), number=10)
            self.issues.append(f"Execution time over 10 runs (timeit): {exec_time:.6f} seconds.")
        except Exception as e:
            self.issues.append(f"Timeit measurement failed: {str(e)}")

        # Utilisation du line_profiler - si activé, mais il nécessite une configuration spécifique
        try:
            from line_profiler import LineProfiler

            profiler = LineProfiler()

            # Ajout d'un profilage ligne par ligne sur le code exécuté
            exec_globals = globals()
            profiler.enable_by_count()

            exec(code, exec_globals)

            profiler.disable()
            s = StringIO()
            profiler.print_stats(stream=s)

            # Ajout des résultats du line_profiler aux issues
            self.issues.append(f"Line-by-line profiling results (line_profiler):\n{s.getvalue()}")

        except ImportError:
            self.issues.append("Line profiling skipped: line_profiler is not installed.")
        except Exception as e:
            self.issues.append(f"Line profiling failed: {str(e)}")


    def run_tests(self):
        """Exécute les tests unitaires et retourne les résultats."""
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(self.test_module)

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
                print(f"Test coverage: {coverage_report}%")

        except Exception as e:
            self.issues.append(f"Test coverage check failed: {str(e)}")

    def check_concurrency_issues(self):
        """Identifie les problèmes de concurrence comme l'accès aux ressources partagées."""
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['acquire', 'release']:
                        self.issues.append(
                            f"Line {node.lineno}: Possible improper use of locks. Ensure proper usage to avoid deadlocks."
                        )

    def check_solid_principles(self):
        """Vérifie le respect des principes SOLID."""
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    # Principe de responsabilité unique (SRP) : Vérifie si la classe a trop de méthodes
                    if len([n for n in node.body if isinstance(n, ast.FunctionDef)]) > 10:
                        self.issues.append(
                            f"Class '{node.name}' at line {node.lineno} might violate the Single Responsibility Principle by having too many methods."
                        )

                    # Principe ouvert/fermé (OCP) : Difficile à vérifier statiquement, mais nous pouvons donner un avertissement général
                    if any(isinstance(n, ast.FunctionDef) and n.name.startswith('_') for n in node.body):
                        self.issues.append(
                            f"Class '{node.name}' at line {node.lineno} might be using too many protected methods. Consider if the class can be extended without modification."
                        )

    def check_type_annotations(self):
        """Vérifie les annotations de type manquantes dans les définitions de fonctions."""
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not node.returns or not all(arg.annotation is not None for arg in node.args.args):
                        self.issues.append(
                            f"Function '{node.name}' at line {node.lineno} is missing type annotations."
                        )

    def check_design_patterns(self):
        """Identifie les modèles de conception utilisés dans le code."""
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())
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
        with open(self.file_path, 'r') as file:
            for line_num, line in enumerate(file, 1):
                for pattern in SECRET_PATTERNS:
                    if re.search(pattern, line):
                        self.issues.append(
                            f"Line {line_num}: Potential secret found in code.")

    def check_code_duplication(self):
        """Identifie les blocs de code dupliqués."""
        #  Implémentation de la détection de code dupliqué
        with open(self.file_path, 'r') as file:
            code = file.read()

        #  Utiliser une technique simple pour identifier les lignes dupliquées
        lines = code.splitlines()
        seen_lines = set()
        for i, line in enumerate(lines):
            if line in seen_lines:
                self.issues.append(
                    f"Line {i+1}: Possible code duplication detected.")
            else:
                seen_lines.add(line)

    def check_error_handling(self):
        """Analyse la gestion des erreurs dans le fichier."""
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())

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
        with open(self.file_path, 'r') as file:
            tree = ast.parse(file.read())

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

# Exemple d'utilisation
if __name__ == "__main__":
    analyzer = StaticAnalyzer(r"C:\Temp\test\compressor.py", "test_compressor")  # Remplacez "example.py" par le chemin de votre fichier
    report = analyzer.analyze()
    print(report)
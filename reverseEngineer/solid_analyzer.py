import ast
import os
from abc import ABC, abstractmethod
class CodeAnalyzer(ABC):
    """
    Interface abstraite pour définir une règle d'analyse de code.
    Chaque règle doit implémenter cette interface.
    """
    @abstractmethod
    def analyze(self, class_node: ast.ClassDef) -> list:
        """
        Analyser une classe AST et retourner une liste d'issues potentielles.
        """
        pass


class SRPAnalyzer(CodeAnalyzer):
    """
    Analyseur du principe de responsabilité unique (SRP).
    Une classe ne doit avoir qu'une seule responsabilité.
    """
    def analyze(self, class_node: ast.ClassDef) -> list:
        issues = []
        class_name = class_node.name
        responsibilities = set()

        # Analyser les méthodes pour détecter les différentes responsabilités
        for method in class_node.body:
            if isinstance(method, ast.FunctionDef):
                method_name = method.name
                if "data" in method_name:
                    responsibilities.add("data_handling")
                elif "email" in method_name:
                    responsibilities.add("email_handling")
                elif "report" in method_name:
                    responsibilities.add("report_generation")
                else:
                    responsibilities.add("other")

        if len(responsibilities) > 2:
            issues.append(f"SRP violation in class {class_name}: Multiple distinct responsibilities detected: {responsibilities}")

        # Vérification supplémentaire basée sur la méthode `check_solid_principles`
        if len([n for n in class_node.body if isinstance(n, ast.FunctionDef)]) > 10:
            issues.append(
                f"Class '{class_name}' at line {class_node.lineno} might violate the SRP by having too many methods."
            )

        return issues


class OCPAnalyzer(CodeAnalyzer):
    """
    Analyseur du principe Open-Closed (OCP).
    Une classe doit être ouverte à l'extension mais fermée à la modification.
    """
    def analyze(self, class_node: ast.ClassDef) -> list:
        issues = []
        class_name = class_node.name
        base_classes = [base.id for base in class_node.bases if isinstance(base, ast.Name)]

        if base_classes:
            issues.append(f"OCP check: Class {class_name} inherits from {base_classes}. Ensure that it extends behavior without modifying base class logic.")

        # Ajouter un avertissement si la classe utilise trop de méthodes protégées
        if any(isinstance(n, ast.FunctionDef) and n.name.startswith('_') for n in class_node.body):
            issues.append(
                f"Class '{class_name}' at line {class_node.lineno} might be using too many protected methods. "
                f"Consider if the class can be extended without modification."
            )

        return issues


class LSPAnalyzer(CodeAnalyzer):
    """
    Analyseur du principe de substitution de Liskov (LSP).
    Vérifie si les sous-classes respectent le contrat de la superclasse.
    """
    def analyze(self, class_node: ast.ClassDef) -> list:
        issues = []
        class_name = class_node.name
        base_classes = [base.id for base in class_node.bases if isinstance(base, ast.Name)]

        if base_classes:
            issues.append(f"LSP check: Class {class_name} inherits from {base_classes}. Verify method overrides respect the base class contract.")
        
        return issues


class ISPAnalyzer(CodeAnalyzer):
    """
    Analyseur du principe de ségrégation des interfaces (ISP).
    Une classe ne doit pas avoir trop de méthodes ou forcer l'implémentation de méthodes inutiles.
    """
    def analyze(self, class_node: ast.ClassDef) -> list:
        issues = []
        class_name = class_node.name
        methods = [n for n in class_node.body if isinstance(n, ast.FunctionDef)]

        if len(methods) > 10:  # Seuil arbitraire
            issues.append(f"ISP violation in class {class_name}: Too many methods ({len(methods)}). Consider refactoring into smaller interfaces.")

        return issues


class DIPAnalyzer(CodeAnalyzer):
    """
    Analyseur du principe d'inversion de dépendance (DIP).
    Vérifie si des implémentations concrètes sont instanciées directement.
    """
    def analyze(self, class_node: ast.ClassDef) -> list:
        issues = []
        
        for method in class_node.body:
            if isinstance(method, ast.FunctionDef):
                for stmt in method.body:
                    if isinstance(stmt, ast.Assign):
                        if isinstance(stmt.value, ast.Call) and isinstance(stmt.value.func, ast.Name):
                            instantiated_class = stmt.value.func.id
                            issues.append(f"DIP violation in method {method.name}: Direct instantiation of {instantiated_class}. Use abstractions/interfaces instead.")
        
        return issues


class SOLIDAnalyzerEngine:
    """
    Moteur d'analyse qui utilise plusieurs analyseurs pour vérifier les principes SOLID.
    Il applique les règles d'analyse sur chaque classe trouvée dans le code.
    """
    def __init__(self, analyzers):
        self.analyzers = analyzers

    def analyze_code(self, code: str) -> list:
        tree = ast.parse(code)
        issues = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for analyzer in self.analyzers:
                    issues.extend(analyzer.analyze(node))
        return issues


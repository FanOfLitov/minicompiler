# test_semantic.py
import sys
from pathlib import Path
from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer

def run_semantic_test(src_file: Path, expected_errors_file: Path = None, verbose=False):
    with open(src_file) as f:
        source = f.read()
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    parser = Parser(tokens)
    ast = parser.parse()
    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(ast)
    error_str = '\n'.join(str(e) for e in errors)
    if expected_errors_file and expected_errors_file.exists():
        expected = expected_errors_file.read_text().strip()
        if error_str.strip() == expected:
            print(f"✓ {src_file.name}")
            return True
        else:
            print(f"✗ {src_file.name}")
            if verbose:
                print("Expected:\n", expected)
                print("Got:\n", error_str)
            return False
    else:
        # Если нет ожидаемого файла, считаем успехом только если нет ошибок
        if not errors:
            print(f"✓ {src_file.name} (no errors)")
            return True
        else:
            print(f"✗ {src_file.name} (unexpected errors)")
            if verbose:
                print(error_str)
            return False

def main():
    # аналогично test_runner.py
    ...
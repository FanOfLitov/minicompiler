#!/usr/bin/env python3
"""Test runner for semantic analysis (Sprint 3)."""

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer


def run_valid_test(src_file: Path, verbose: bool = False) -> bool:
    """
    Запускает семантический анализ на валидной программе.
    Ожидается, что ошибок нет.
    """
    try:
        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print(f"✗ {src_file.name}: cannot read file - {e}")
        return False

    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    # Если лексер нашёл ошибки, тест провален (для валидных программ лексер должен работать)
    if any(t.type.name == 'ERROR' for t in tokens):
        print(f"✗ {src_file.name}: lexer errors found")
        if verbose:
            print("\n".join(str(t) for t in tokens if t.type.name == 'ERROR'))
        return False

    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except Exception as e:
        print(f"✗ {src_file.name}: parse error - {e}")
        return False

    analyzer = SemanticAnalyzer()
    errors = analyzer.analyze(ast)

    if errors:
        print(f"✗ {src_file.name}: semantic errors found")
        if verbose:
            for err in errors:
                print(f"  {err}")
        return False
    else:
        print(f"✓ {src_file.name}")
        return True


def run_invalid_test(src_file: Path, expected_file: Path, verbose: bool = False) -> bool:
    """
    Запускает семантический анализ на программе, которая должна содержать ошибки.
    Сравнивает фактические сообщения об ошибках с ожидаемыми (файл .expected).
    """
    try:
        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print(f"✗ {src_file.name}: cannot read file - {e}")
        return False

    scanner = Scanner(source)
    tokens = scanner.scan_tokens()
    # Для невалидных программ лексер может тоже давать ошибки – их тоже учитываем
    lexer_errors = [str(t) for t in tokens if t.type.name == 'ERROR']

    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except Exception as e:
        # Если парсер упал, считаем это ошибкой (но в некоторых тестах может быть и так)
        print(f"✗ {src_file.name}: parse error - {e}")
        return False

    analyzer = SemanticAnalyzer()
    semantic_errors = analyzer.analyze(ast)

    # Собираем все ошибки: сначала лексера, потом семантические
    all_errors = lexer_errors + [str(e) for e in semantic_errors]
    actual = "\n".join(all_errors).strip()

    if not expected_file.exists():
        print(f"✗ {src_file.name}: expected file {expected_file} not found")
        return False

    expected = expected_file.read_text(encoding='utf-8').strip()

    if actual == expected:
        print(f"✓ {src_file.name}")
        return True
    else:
        print(f"✗ {src_file.name}")
        if verbose:
            print("Expected errors:")
            print(expected)
            print("Actual errors:")
            print(actual)
        return False


def generate_expected_outputs():
    """Генерирует эталонные файлы для invalid тестов (один раз, вручную)."""
    invalid_dir = Path("tests/semantic/invalid")
    for src_file in sorted(invalid_dir.glob("**/*.src")):
        expected_file = src_file.with_suffix(".expected")
        # Прогоняем тест и сохраняем вывод ошибок
        with open(src_file, 'r', encoding='utf-8') as f:
            source = f.read()
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()
        lexer_errors = [str(t) for t in tokens if t.type.name == 'ERROR']
        parser = Parser(tokens)
        ast = parser.parse()
        analyzer = SemanticAnalyzer()
        semantic_errors = analyzer.analyze(ast)
        all_errors = lexer_errors + [str(e) for e in semantic_errors]
        output = "\n".join(all_errors).strip()
        expected_file.write_text(output + "\n", encoding='utf-8')
        print(f"Generated: {expected_file}")
    print("Done.")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Semantic analysis test runner")
    parser.add_argument("--generate", action="store_true",
                        help="Generate expected output files for invalid tests")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed output on failures")
    parser.add_argument("--test", type=str,
                        help="Run a specific test file (e.g., tests/semantic/valid/foo.src)")
    args = parser.parse_args()

    if args.generate:
        generate_expected_outputs()
        return

    if args.test:
        test_path = Path(args.test)
        if not test_path.exists():
            print(f"Test file not found: {test_path}")
            sys.exit(1)
        if "valid" in test_path.parts:
            success = run_valid_test(test_path, args.verbose)
        else:
            expected = test_path.with_suffix(".expected")
            success = run_invalid_test(test_path, expected, args.verbose)
        sys.exit(0 if success else 1)

    # Запуск всех тестов
    valid_dir = Path("tests/semantic/valid")
    invalid_dir = Path("tests/semantic/invalid")
    passed = 0
    failed = 0

    print("Valid semantic tests:")
    for src_file in sorted(valid_dir.glob("**/*.src")):
        if run_valid_test(src_file, args.verbose):
            passed += 1
        else:
            failed += 1

    print("\nInvalid semantic tests (expecting errors):")
    for src_file in sorted(invalid_dir.glob("**/*.src")):
        expected_file = src_file.with_suffix(".expected")
        if run_invalid_test(src_file, expected_file, args.verbose):
            passed += 1
        else:
            failed += 1

    print(f"\nPassed: {passed}, Failed: {failed}")
    sys.exit(0 if failed == 0 else 1)


if __name__ == "__main__":
    main()
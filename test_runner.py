import os
import sys
import subprocess
from pathlib import Path


def run_lexer_test(test_file: Path, expected_file: Path = None, verbose: bool = False):
    """Запускает лексер на тестовом файле и сравнивает результат с ожидаемым."""

    # Читаем исходный код
    with open(test_file, 'r', encoding='utf-8') as f:
        source = f.read()

    # Импортируем и запускаем сканер
    from src.lexer.scanner import Scanner
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    # Формируем вывод
    output = '\n'.join(str(token) for token in tokens)

    if expected_file and expected_file.exists():
        # Сравниваем с ожидаемым результатом
        with open(expected_file, 'r', encoding='utf-8') as f:
            expected = f.read().strip()

        actual = output.strip()

        if actual == expected:
            print(f"✓ {test_file.name}")
            return True
        else:
            print(f"✗ {test_file.name}")
            if verbose:
                print(f"Expected:\n{expected}")
                print(f"Actual:\n{actual}")
                print("-" * 50)
            return False
    else:
        # Просто выводим результат
        print(f"Test: {test_file.name}")
        print(output)
        print("-" * 50)
        return True


def run_all_tests():
    """Запускает все тесты."""

    base_dir = Path("tests/lexer")
    valid_dir = base_dir / "valid"
    invalid_dir = base_dir / "invalid"

    print("=" * 60)
    print("Running Lexer Tests")
    print("=" * 60)

    passed = 0
    failed = 0

    # Валидные тесты
    print("\nValid Tests:")
    print("-" * 40)

    for test_file in sorted(valid_dir.glob("*.src")):
        expected_file = test_file.with_suffix('.txt')

        if run_lexer_test(test_file, expected_file):
            passed += 1
        else:
            failed += 1

    # Невалидные тесты (ожидаем ошибки)
    print("\nInvalid Tests (expecting errors):")
    print("-" * 40)

    for test_file in sorted(invalid_dir.glob("*.src")):
        # Для невалидных тестов просто проверяем, что лексер не падает
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                source = f.read()

            from src.lexer.scanner import Scanner
            scanner = Scanner(source)
            tokens = scanner.scan_tokens()

            # Проверяем, есть ли токены ошибок
            has_errors = any(token.type.name == 'ERROR' for token in tokens)

            if has_errors:
                print(f"✓ {test_file.name} (error detected)")
                passed += 1
            else:
                print(f"✗ {test_file.name} (no error detected)")
                failed += 1

        except Exception as e:
            print(f"✗ {test_file.name} (crashed: {e})")
            failed += 1

    # Итоги
    print("\n" + "=" * 60)
    print(f"Total: {passed + failed}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print("=" * 60)

    return failed == 0


def generate_expected_output():
    """Генерирует ожидаемые выходные файлы для валидных тестов."""

    valid_dir = Path("tests/lexer/valid")

    print("Generating expected output files...")

    for test_file in sorted(valid_dir.glob("*.src")):
        expected_file = test_file.with_suffix('.txt')

        with open(test_file, 'r', encoding='utf-8') as f:
            source = f.read()

        from src.lexer.scanner import Scanner
        scanner = Scanner(source)
        tokens = scanner.scan_tokens()

        output = '\n'.join(str(token) for token in tokens)

        with open(expected_file, 'w', encoding='utf-8') as f:
            f.write(output + '\n')

        print(f"Generated: {expected_file.name}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test runner for MiniCompiler lexer")
    parser.add_argument("--generate", action="store_true",
                        help="Generate expected output files")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show detailed output on failures")
    parser.add_argument("--test", type=str,
                        help="Run specific test file")

    args = parser.parse_args()

    if args.generate:
        generate_expected_output()
        return

    if args.test:
        test_file = Path(args.test)
        if not test_file.exists():
            print(f"Test file not found: {args.test}")
            sys.exit(1)

        expected_file = test_file.with_suffix('.txt')
        success = run_lexer_test(test_file, expected_file if expected_file.exists() else None, args.verbose)
        sys.exit(0 if success else 1)

    success = run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
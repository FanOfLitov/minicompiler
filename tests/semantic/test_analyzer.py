"""
Data-driven (Golden) and Unit tests for the Semantic Analyzer.
Compatible with Python 3.8+ and Windows.
"""
import pytest
from pathlib import Path
from typing import List
from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer

SEMANTIC_DIR = Path(__file__).resolve().parent
VALID_DIR = SEMANTIC_DIR / "valid"
INVALID_DIR = SEMANTIC_DIR / "invalid"


# ─── Автоматические тесты на файлах (Golden Tests) ─────────────────────────

def get_valid_files() -> List[Path]:
    if not VALID_DIR.exists():
        return []
    return sorted(list(VALID_DIR.glob("*.src")))


def get_invalid_files() -> List[Path]:
    if not INVALID_DIR.exists():
        return []
    return sorted(list(INVALID_DIR.glob("*.src")))


@pytest.mark.parametrize("src_path", get_valid_files())
def test_semantic_golden_valid(src_path: Path):
    source = src_path.read_text(encoding="utf-8")

    scanner = Scanner(source, filename=src_path.name)
    tokens = scanner.scan_all()
    parser = Parser(tokens)
    program = parser.parse()

    assert program is not None, f"Parse failed for {src_path.name}"

    analyzer = SemanticAnalyzer(filename=src_path.name, source=source)
    success = analyzer.analyze(program)

    assert success, f"Expected clean semantic analysis for {src_path.name}, but got errors:\n{analyzer.format_errors()}"


@pytest.mark.parametrize("src_path", get_invalid_files())
def test_semantic_golden_invalid(src_path: Path):
    expected_path = src_path.with_suffix(".expected")
    source = src_path.read_text(encoding="utf-8")

    scanner = Scanner(source, filename=src_path.name)
    tokens = scanner.scan_all()
    parser = Parser(tokens)
    program = parser.parse()

    assert program is not None, f"Parse failed for invalid semantic test {src_path.name}"

    analyzer = SemanticAnalyzer(filename=src_path.name, source=source)
    success = analyzer.analyze(program)

    assert not success, f"Expected semantic errors in {src_path.name}, but validation passed successfully."

    if expected_path.exists():
        expected_errors = expected_path.read_text(encoding="utf-8").strip().replace("\r\n", "\n")

        # Получаем и очищаем сообщения об ошибках от платформозависимых путей
        actual_errors = "\n".join([str(e) for e in analyzer.errors]).strip().replace("\r\n", "\n")

        # Нормализуем сравнение строк
        actual_lines = [line.strip() for line in actual_errors.splitlines()]
        expected_lines = [line.strip() for line in expected_errors.splitlines()]

        # Проверяем, что ключевое сообщение об ошибке содержится в выводе
        for exp in expected_lines:
            assert any(exp in act for act in actual_lines), f"Expected error comment '{exp}' was not found in actual errors of {src_path.name}"


# ─── Статические Юнит-Тесты (Fallback) ─────────────────────────────────────

def test_basic_semantic_mismatch():
    source = "fn main() { int x = \"string\"; }"
    scanner = Scanner(source)
    parser = Parser(scanner.scan_all())
    program = parser.parse()
    analyzer = SemanticAnalyzer(source=source)
    success = analyzer.analyze(program)
    assert not success
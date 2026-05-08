
import pytest
from pathlib import Path
from typing import List
from src.lexer.token_types import TokenType, Token
from src.lexer.scanner import Scanner

# Определение путей к файлам тестов
LEXER_DIR = Path(__file__).resolve().parent
VALID_DIR = LEXER_DIR / "valid"
INVALID_DIR = LEXER_DIR / "invalid"


def format_token_canonical(tok: Token) -> str:
    """Formats a token to match the expected .txt test files."""
    # Шаблон: LINE:COLUMN TOKEN_TYPE "LEXEME" [LITERAL_VALUE]
    if tok.type in {TokenType.INT_LITERAL, TokenType.FLOAT_LITERAL, TokenType.STRING_LITERAL, TokenType.BOOL_LITERAL}:
        if tok.type == TokenType.STRING_LITERAL:
            return f'{tok.line}:{tok.column} {tok.type.name} "{tok.lexeme}" "{tok.literal}"'
        elif tok.type == TokenType.BOOL_LITERAL:
            val_str = "true" if tok.literal else "false"
            return f'{tok.line}:{tok.column} {tok.type.name} "{tok.lexeme}" {val_str}'
        else:
            return f'{tok.line}:{tok.column} {tok.type.name} "{tok.lexeme}" {tok.literal}'
    else:
        return f'{tok.line}:{tok.column} {tok.type.name} "{tok.lexeme}"'


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
def test_lexer_golden_valid(src_path: Path):
    txt_path = src_path.with_suffix(".txt")
    assert txt_path.exists(), f"Missing expected token file: {txt_path}"

    source = src_path.read_text(encoding="utf-8")
    expected_content = txt_path.read_text(encoding="utf-8").strip().replace("\r\n", "\n")

    scanner = Scanner(source, filename=src_path.name)
    tokens = scanner.scan_all()

    assert len(scanner.errors) == 0, f"Expected no errors in {src_path.name}, got: {[str(e) for e in scanner.errors]}"

    # Форматируем полученные токены
    actual_lines = [format_token_canonical(t) for t in tokens]
    actual_content = "\n".join(actual_lines).strip()

    assert actual_content == expected_content, f"Token mismatch in {src_path.name}"


@pytest.mark.parametrize("src_path", get_invalid_files())
def test_lexer_golden_invalid(src_path: Path):
    source = src_path.read_text(encoding="utf-8")
    scanner = Scanner(source, filename=src_path.name)
    scanner.scan_all()

    assert len(scanner.errors) > 0, f"Expected lexical errors in invalid file: {src_path.name}"


# ─── Статические Юнит-Тесты (Fallback) ─────────────────────────────────────

def test_basic_scanner_logic():
    s = Scanner("int x = 42;")
    tokens = s.scan_all()
    assert len(tokens) == 6  # int, x, =, 42, ;, EOF
    assert tokens[0].type == TokenType.KW_INT
    assert tokens[1].lexeme == "x"
    assert tokens[3].literal == 42
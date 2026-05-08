
from __future__ import annotations

from typing import List, Optional, Union, Dict, Set, Tuple
from .token_types import Token, TokenType, KEYWORDS

MAX_IDENTIFIER_LENGTH = 255
INT_MIN = -(2 ** 31)
INT_MAX = 2 ** 31 - 1


class LexerError:
    def __init__(self, message: str, line: int, column: int) -> None:
        self.message = message
        self.line    = line
        self.column  = column

    def __str__(self) -> str:
        return f"lexer error at {self.line}:{self.column}: {self.message}"


class Scanner:
    def __init__(self, source: str, filename: str = "<unknown>") -> None:
        self._source:   str          = source
        self._filename: str          = filename
        self._tokens:   List[Token]  = []
        self.errors:    List[LexerError] = []

        self._start:    int = 0
        self._current:  int = 0
        self._line:     int = 1
        self._col_start: int = 1
        self._col:      int = 1

    def scan_all(self) -> List[Token]:
        while not self._is_at_end():
            self._start      = self._current
            self._col_start  = self._col
            self._scan_token()

        self._tokens.append(
            Token(TokenType.EOF, "", self._line, self._col)
        )
        return self._tokens

    def _scan_token(self) -> None:
        c = self._advance()

        if c in (' ', '\t', '\r'):
            return
        if c == '\n':
            return

        if c == '(':
            self._add_token(TokenType.LPAREN)
        elif c == ')':
            self._add_token(TokenType.RPAREN)
        elif c == '{':
            self._add_token(TokenType.LBRACE)
        elif c == '}':
            self._add_token(TokenType.RBRACE)
        elif c == '[':
            self._add_token(TokenType.LBRACKET)
        elif c == ']':
            self._add_token(TokenType.RBRACKET)
        elif c == ';':
            self._add_token(TokenType.SEMICOLON)
        elif c == ',':
            self._add_token(TokenType.COMMA)
        elif c == ':':
            self._add_token(TokenType.COLON)
        elif c == '%':
            self._add_token(TokenType.PERCENT)
        elif c == '*':
            self._add_token(TokenType.STAR_ASSIGN if self._match('=') else TokenType.STAR)
        elif c == '+':
            self._add_token(TokenType.PLUS_ASSIGN if self._match('=') else TokenType.PLUS)
        elif c == '!':
            self._add_token(TokenType.BANG_EQ if self._match('=') else TokenType.BANG)
        elif c == '=':
            self._add_token(TokenType.EQ_EQ if self._match('=') else TokenType.ASSIGN)
        elif c == '<':
            self._add_token(TokenType.LT_EQ if self._match('=') else TokenType.LT)
        elif c == '>':
            self._add_token(TokenType.GT_EQ if self._match('=') else TokenType.GT)
        elif c == '&':
            if self._match('&'):
                self._add_token(TokenType.AMP_AMP)
            else:
                self._error("unexpected character '&'; did you mean '&&'?")
        elif c == '|':
            if self._match('|'):
                self._add_token(TokenType.PIPE_PIPE)
            else:
                self._error("unexpected character '|'; did you mean '||'?")
        elif c == '-':
            if self._match('>'):
                self._add_token(TokenType.ARROW)
            elif self._match('='):
                self._add_token(TokenType.MINUS_ASSIGN)
            else:
                self._add_token(TokenType.MINUS)
        elif c == '/':
            if self._match('/'):
                self._skip_line_comment()
            elif self._match('*'):
                self._skip_block_comment()
            elif self._match('='):
                self._add_token(TokenType.SLASH_ASSIGN)
            else:
                self._add_token(TokenType.SLASH)
        elif c == '"':
            self._scan_string()
        elif c == '.':
            # Поддержка чисел, начинающихся с точки, например .5
            if self._peek().isdigit():
                self._scan_float_starting_with_dot()
            else:
                self._error("unexpected character '.'")
        else:
            if c.isdigit():
                self._scan_number(c)
            elif c.isalpha() or c == '_':
                self._scan_identifier()
            else:
                self._error(f"unexpected character {c!r}")

    def _skip_line_comment(self) -> None:
        while not self._is_at_end() and self._peek() != '\n':
            self._advance()

    def _skip_block_comment(self) -> None:
        start_line = self._line
        start_col  = self._col_start
        depth = 1

        while not self._is_at_end() and depth > 0:
            c = self._advance()
            if c == '/' and self._peek() == '*':
                self._advance()
                depth += 1
            elif c == '*' and self._peek() == '/':
                self._advance()
                depth -= 1

        if depth > 0:
            self._errors_at(
                start_line, start_col,
                "unterminated block comment (/* ... */ not closed)"
            )

    def _scan_string(self) -> None:
        start_line = self._line
        start_col  = self._col_start
        chars: List[str] = []

        while not self._is_at_end() and self._peek() != '"':
            c = self._advance()
            if c == '\n':
                self._errors_at(
                    start_line, start_col,
                    "unterminated string literal (newline before closing '\"')"
                )
                return
            if c == '\\':
                escape = self._advance() if not self._is_at_end() else ''
                if escape == 'n':
                    chars.append('\n')
                elif escape == 't':
                    chars.append('\t')
                elif escape == 'r':
                    chars.append('\r')
                elif escape == '\\':
                    chars.append('\\')
                elif escape == '"':
                    chars.append('"')
                elif escape == '0':
                    chars.append('\0')
                else:
                    self._error(f"unknown escape sequence '\\{escape}'")
                    chars.append(escape)
            else:
                chars.append(c)

        if self._is_at_end():
            self._errors_at(
                start_line, start_col,
                "unterminated string literal (reached end of file)"
            )
            return

        self._advance()
        value = ''.join(chars)
        lexeme = self._source[self._start:self._current]
        self._tokens.append(
            Token(TokenType.STRING_LITERAL, lexeme,
                  start_line, start_col, value)
        )

    def _scan_number(self, first: str) -> None:
        while not self._is_at_end() and self._peek().isdigit():
            self._advance()

        is_float = False
        if (not self._is_at_end() and self._peek() == '.'
                and self._peek_next().isdigit()):
            is_float = True
            self._advance()
            while not self._is_at_end() and self._peek().isdigit():
                self._advance()

        lexeme = self._source[self._start:self._current]

        # Ошибка: идентификатор начинается с цифры (например, 1abc)
        if not self._is_at_end() and (self._peek().isalpha() or self._peek() == '_'):
            while not self._is_at_end() and (self._peek().isalnum() or self._peek() == '_'):
                self._advance()
            full_lexeme = self._source[self._start:self._current]
            self._errors_at(self._line, self._col_start, f"invalid identifier starting with digit: '{full_lexeme}'")
            return

        if is_float:
            value = float(lexeme)
            self._tokens.append(
                Token(TokenType.FLOAT_LITERAL, lexeme,
                      self._line, self._col_start, value)
            )
        else:
            value = int(lexeme)
            if not (INT_MIN <= value <= INT_MAX):
                self._error(
                    f"integer literal {value} is out of range "
                    f"[{INT_MIN}, {INT_MAX}]"
                )
            self._tokens.append(
                Token(TokenType.INT_LITERAL, lexeme,
                      self._line, self._col_start, value)
            )

    def _scan_float_starting_with_dot(self) -> None:
        # Разбор чисел типа .5
        while not self._is_at_end() and self._peek().isdigit():
            self._advance()
        lexeme = self._source[self._start:self._current]
        self._tokens.append(
            Token(TokenType.FLOAT_LITERAL, lexeme,
                  self._line, self._col_start, float(lexeme))
        )

    def _scan_identifier(self) -> None:
        while not self._is_at_end() and (
            self._peek().isalnum() or self._peek() == '_'
        ):
            self._advance()

        lexeme = self._source[self._start:self._current]

        if len(lexeme) > MAX_IDENTIFIER_LENGTH:
            self._error(
                f"identifier '{lexeme[:20]}...' exceeds maximum length "
                f"of {MAX_IDENTIFIER_LENGTH} characters"
            )

        ttype = KEYWORDS.get(lexeme)
        if ttype is not None:
            if ttype == TokenType.KW_TRUE:
                self._tokens.append(
                    Token(TokenType.BOOL_LITERAL, lexeme,
                          self._line, self._col_start, True)
                )
            elif ttype == TokenType.KW_FALSE:
                self._tokens.append(
                    Token(TokenType.BOOL_LITERAL, lexeme,
                          self._line, self._col_start, False)
                )
            else:
                self._tokens.append(
                    Token(ttype, lexeme, self._line, self._col_start)
                )
        else:
            self._tokens.append(
                Token(TokenType.IDENTIFIER, lexeme,
                      self._line, self._col_start)
            )

    def _is_at_end(self) -> bool:
        return self._current >= len(self._source)

    def _advance(self) -> str:
        ch = self._source[self._current]
        self._current += 1

        if ch == '\n':
            self._line += 1
            self._col = 1
        else:
            self._col += 1

        return ch

    def _peek(self) -> str:
        if self._is_at_end():
            return '\0'
        return self._source[self._current]

    def _peek_next(self) -> str:
        if self._current + 1 >= len(self._source):
            return '\0'
        return self._source[self._current + 1]

    def _match(self, expected: str) -> bool:
        if self._is_at_end() or self._source[self._current] != expected:
            return False
        self._advance()
        return True

    def _add_token(self, ttype: TokenType,
                   literal: object = None) -> None:
        lexeme = self._source[self._start:self._current]
        self._tokens.append(
            Token(ttype, lexeme, self._line, self._col_start, literal)
        )

    def _error(self, message: str) -> None:
        self._errors_at(self._line, self._col_start, message)

    def _errors_at(self, line: int, col: int, message: str) -> None:
        self.errors.append(LexerError(message, line, col))
        lexeme = self._source[self._start:self._current]
        self._tokens.append(
            Token(TokenType.ERROR, lexeme, line, col)
        )
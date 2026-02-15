import re
from .token import Token, TokenType
from typing import Any, List

class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens: list[Token] = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.column = 1
        self.start_column = 1

        self.keywords = {
            'if': TokenType.KW_IF,
            'else': TokenType.KW_ELSE,
            'while': TokenType.KW_WHILE,
            'for': TokenType.KW_FOR,
            'int': TokenType.KW_INT,
            'float': TokenType.KW_FLOAT,
            'bool': TokenType.KW_BOOL,
            'return': TokenType.KW_RETURN,
            'true': TokenType.KW_TRUE,
            'false': TokenType.KW_FALSE,
            'void': TokenType.KW_VOID,
            'struct': TokenType.KW_STRUCT,
            'fn': TokenType.KW_FN,
        }

    def is_at_end(self) -> bool:
        return self.current >= len(self.source)

    def advance(self) -> str:
        char = self.source[self.current]
        self.current += 1
        self.column += 1
        return char

    def peek(self) -> str:
        return '\0' if self.is_at_end() else self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def match(self, expected: str) -> bool:
        if self.is_at_end() or self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def add_token(self, token_type: TokenType, literal: Any = None):
        lexeme = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, lexeme, self.line, self.start_column, literal))

    def scan_tokens(self) -> list[Token]:
        while not self.is_at_end():
            self.start = self.current
            self.start_column = self.column
            self.scan_token()

        self.tokens.append(Token(TokenType.END_OF_FILE, "", self.line, self.column))
        return self.tokens

    def scan_token(self):
        char = self.advance()

        # Пробелы
        if char in ' \t\r':
            return
        if char == '\n':
            self.line += 1
            self.column = 1
            return

        # Комментарии
        if char == '/':
            if self.match('/'):
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
                return
            if self.match('*'):
                self.block_comment()
                return
            if self.match('='):
                self.add_token(TokenType.SLASH_ASSIGN)
                return
            self.add_token(TokenType.SLASH)
            return

        # Операторы
        if char == '+': self.add_token(TokenType.PLUS_ASSIGN if self.match('=') else TokenType.PLUS)
        elif char == '-': self.add_token(TokenType.MINUS_ASSIGN if self.match('=') else TokenType.MINUS)
        elif char == '*': self.add_token(TokenType.STAR_ASSIGN if self.match('=') else TokenType.STAR)
        elif char == '%': self.add_token(TokenType.PERCENT)
        elif char == '=': self.add_token(TokenType.EQ if self.match('=') else TokenType.ASSIGN)
        elif char == '!': self.add_token(TokenType.NE if self.match('=') else TokenType.NOT)
        elif char == '<': self.add_token(TokenType.LE if self.match('=') else TokenType.LT)
        elif char == '>': self.add_token(TokenType.GE if self.match('=') else TokenType.GT)
        elif char == '&': self.add_token(TokenType.AND) if self.match('&') else self.error("Unexpected '&'")
        elif char == '|': self.add_token(TokenType.OR) if self.match('|') else self.error("Unexpected '|'")

        # Делимитеры
        elif char == '(': self.add_token(TokenType.LPAREN)
        elif char == ')': self.add_token(TokenType.RPAREN)
        elif char == '{': self.add_token(TokenType.LBRACE)
        elif char == '}': self.add_token(TokenType.RBRACE)
        elif char == '[': self.add_token(TokenType.LBRACKET)
        elif char == ']': self.add_token(TokenType.RBRACKET)
        elif char == ';': self.add_token(TokenType.SEMICOLON)
        elif char == ',': self.add_token(TokenType.COMMA)
        elif char == ':': self.add_token(TokenType.COLON)
        elif char == '.': self.add_token(TokenType.DOT)

        # Строки
        elif char == '"':
            self.string()

        # Числа
        elif char.isdigit():
            self.number()

        # Идентификаторы / ключевые слова
        elif char.isalpha() or char == '_':
            self.identifier()

        else:
            self.error(f"Unexpected character: '{char}'")

    def block_comment(self):
        while not self.is_at_end():
            if self.peek() == '*' and self.peek_next() == '/':
                self.advance()  # *
                self.advance()  # /
                return
            if self.peek() == '\n':
                self.line += 1
                self.column = 1
            self.advance()
        self.error("Unterminated block comment")

    def string(self):
        while self.peek() != '"' and not self.is_at_end():
            if self.peek() == '\n':
                self.line += 1
                self.column = 1
            self.advance()

        if self.is_at_end():
            self.error("Unterminated string")
            return

        self.advance()  # закрывающая "
        literal = self.source[self.start + 1:self.current - 1]
        self.add_token(TokenType.STRING_LITERAL, literal)

    def number(self):
        while self.peek().isdigit():
            self.advance()

        if self.peek() == '.' and self.peek_next().isdigit():
            self.advance()  # .
            while self.peek().isdigit():
                self.advance()
            literal = float(self.source[self.start:self.current])
            self.add_token(TokenType.FLOAT_LITERAL, literal)
        else:
            literal = int(self.source[self.start:self.current])
            self.add_token(TokenType.INT_LITERAL, literal)

    def identifier(self):
        while self.peek().isalnum() or self.peek() == '_':
            self.advance()
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)

    def error(self, message: str):
        print(f"Error at line {self.line}, column {self.column}: {message}")
        self.add_token(TokenType.ERROR, message)
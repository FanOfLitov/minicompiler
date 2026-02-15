import re
from .token import Token, TokenType

class Scanner:
    def __init__(self, source: str):
        self.source = source
        self.tokens = []          # список всех токенов
        self.start = 0             # начало текущего лексемы
        self.current = 0           # текущая позиция в строке
        self.line = 1
        self.column = 1


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
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self) -> str:
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def match(self, expected: str) -> bool:
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        self.column += 1
        return True

    def add_token(self, token_type: TokenType, literal: any = None):
        lexeme = self.source[self.start:self.current]
        self.tokens.append(Token(token_type, lexeme, self.line, self.start_column, literal))

    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.start_column = self.column   # запоминаем колонку начала токена
            self.scan_token()
        self.tokens.append(Token(TokenType.END_OF_FILE, "", self.line, self.column))
        return self.tokens

    def scan_token(self):
        char = self.advance()
        if char == ' ' or char == '\t' or char == '\r':
            pass
        elif char == '\n':
            self.line += 1
            self.column = 1
        elif char == '/':
            if self.match('/'):
                while self.peek() != '\n' and not self.is_at_end():
                    self.advance()
            elif self.match('*'):
                self.block_comment()
            elif self.match('='):
                self.add_token(TokenType.SLASH_ASSIGN)
            else:
                self.add_token(TokenType.SLASH)
        elif char == '*':
            if self.match('='):
                self.add_token(TokenType.STAR_ASSIGN)
            else:
                self.add_token(TokenType.STAR)
        elif char == '+':
            if self.match('='):
                self.add_token(TokenType.PLUS_ASSIGN)
            else:
                self.add_token(TokenType.PLUS)
        elif char == '-':
            if self.match('='):
                self.add_token(TokenType.MINUS_ASSIGN)
            else:
                self.add_token(TokenType.MINUS)
        elif char == '%':
            self.add_token(TokenType.PERCENT)
        elif char == '=':
            if self.match('='):
                self.add_token(TokenType.EQ)
            else:
                self.add_token(TokenType.ASSIGN)
        elif char == '!':
            if self.match('='):
                self.add_token(TokenType.NE)
            else:
                self.add_token(TokenType.NOT)
        elif char == '<':
            if self.match('='):
                self.add_token(TokenType.LE)
            else:
                self.add_token(TokenType.LT)
        elif char == '>':
            if self.match('='):
                self.add_token(TokenType.GE)
            else:
                self.add_token(TokenType.GT)
        elif char == '&':
            if self.match('&'):
                self.add_token(TokenType.AND)
            else:
                self.error("Unexpected character '&'")
        elif char == '|':
            if self.match('|'):
                self.add_token(TokenType.OR)
            else:
                self.error("Unexpected character '|'")
        elif char == '(':
            self.add_token(TokenType.LPAREN)
        elif char == ')':
            self.add_token(TokenType.RPAREN)
        elif char == '{':
            self.add_token(TokenType.LBRACE)
        elif char == '}':
            self.add_token(TokenType.RBRACE)
        elif char == '[':
            self.add_token(TokenType.LBRACKET)
        elif char == ']':
            self.add_token(TokenType.RBRACKET)
        elif char == ';':
            self.add_token(TokenType.SEMICOLON)
        elif char == ':':
            self.add_token(TokenType.COLON)
        elif char == ',':
            self.add_token(TokenType.COMMA)
        elif char == '.':
            self.add_token(TokenType.DOT)
        elif char == '"':
            self.string()
        elif self.is_digit(char):
            self.number()
        elif self.is_alpha(char):
            self.identifier()
        else:
            self.error(f"Unexpected character: '{char}'")

    # --- Обработка составных конструкций ---
    def block_comment(self):
        """Обрабатывает многострочный комментарий /* ... */ (без вложенности)."""
        while not self.is_at_end():
            if self.peek() == '*' and self.peek_next() == '/':
                self.advance()  # съедаем *
                self.advance()  # съедаем /
                return
            elif self.peek() == '\n':
                self.line += 1
                self.column = 1
                self.advance()
            else:
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
        self.advance()
        literal = self.source[self.start+1:self.current-1]
        self.add_token(TokenType.STRING_LITERAL, literal)

    def number(self):
        while self.is_digit(self.peek()):
            self.advance()
        # Смотрим, есть ли дробная часть
        if self.peek() == '.' and self.is_digit(self.peek_next()):
            # Это float
            self.advance()  # съедаем точку
            while self.is_digit(self.peek()):
                self.advance()
            literal = float(self.source[self.start:self.current])
            self.add_token(TokenType.FLOAT_LITERAL, literal)
        else:
            literal = int(self.source[self.start:self.current])
            self.add_token(TokenType.INT_LITERAL, literal)

    def identifier(self):
        while self.is_alpha_numeric(self.peek()):
            self.advance()
        text = self.source[self.start:self.current]
        token_type = self.keywords.get(text, TokenType.IDENTIFIER)
        self.add_token(token_type)

    def is_digit(self, c: str) -> bool:
        return c.isdigit()

    def is_alpha(self, c: str) -> bool:
        return c.isalpha() or c == '_'

    def is_alpha_numeric(self, c: str) -> bool:
        return self.is_alpha(c) or self.is_digit(c)

    def error(self, message: str):
        print(f"Error at line {self.line}, column {self.column}: {message}")
        self.add_token(TokenType.ERROR, message)

from enum import Enum, auto
from typing import Any, Union

class TokenType(Enum):
    # Ключевые слова (должны соответствовать списку из LANG-2)
    KW_IF = auto()
    KW_ELSE = auto()
    KW_WHILE = auto()
    KW_FOR = auto()
    KW_INT = auto()
    KW_FLOAT = auto()
    KW_BOOL = auto()
    KW_RETURN = auto()
    KW_TRUE = auto()
    KW_FALSE = auto()
    KW_VOID = auto()
    KW_STRUCT = auto()
    KW_FN = auto()

    # Идентификаторы и литералы
    IDENTIFIER = auto()
    INT_LITERAL = auto()
    FLOAT_LITERAL = auto()
    STRING_LITERAL = auto()
    BOOL_LITERAL = auto()  # true/false уже keywords, но можно и так

    # Операторы (односимвольные)
    PLUS = auto()      # +
    MINUS = auto()     # -
    STAR = auto()      # *
    SLASH = auto()     # /
    PERCENT = auto()   # %
    ASSIGN = auto()    # =
    LT = auto()        # <
    GT = auto()        # >
    NOT = auto()       # !
    AMPERSAND = auto() # &
    PIPE = auto()      # |
    LPAREN = auto()    # (
    RPAREN = auto()    # )
    LBRACE = auto()    # {
    RBRACE = auto()    # }
    LBRACKET = auto()  # [
    RBRACKET = auto()  # ]
    SEMICOLON = auto() # ;
    COLON = auto()     # :
    COMMA = auto()     # ,
    DOT = auto()       # .

    # Многосимвольные операторы
    EQ = auto()        # ==
    NE = auto()        # !=
    LE = auto()        # <=
    GE = auto()        # >=
    AND = auto()       # &&
    OR = auto()        # ||
    PLUS_ASSIGN = auto()   # +=
    MINUS_ASSIGN = auto()  # -=
    STAR_ASSIGN = auto()   # *=
    SLASH_ASSIGN = auto()  # /=

    # Специальные
    END_OF_FILE = auto()
    ERROR = auto()

class Token:
    def __init__(self, type: TokenType, lexeme: str, line: int, column: int, literal: Any = None):
        self.type = type
        self.lexeme = lexeme
        self.line = line
        self.column = column
        self.literal = literal  # для чисел и строк – преобразованное значение

    def __repr__(self):
        # Формат: LINE:COLUMN TOKEN_TYPE "LEXEME" [LITERAL_VALUE]
        literal_str = f" {self.literal}" if self.literal is not None else ""
        return f"{self.line}:{self.column} {self.type.name} \"{self.lexeme}\"{literal_str}"

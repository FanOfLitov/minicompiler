"""
Token type definitions for Python 3.8+.
"""
from enum import Enum
from dataclasses import dataclass, field
from typing import Union, Optional, Dict

class TokenType(Enum):
    KW_IF       = "if"
    KW_ELSE     = "else"
    KW_WHILE    = "while"
    KW_FOR      = "for"
    KW_INT      = "int"
    KW_FLOAT    = "float"
    KW_BOOL     = "bool"
    KW_RETURN   = "return"
    KW_TRUE     = "true"
    KW_FALSE    = "false"
    KW_VOID     = "void"
    KW_STRUCT   = "struct"
    KW_FN       = "fn"
    KW_NULL     = "null"

    IDENTIFIER  = "IDENTIFIER"

    INT_LITERAL    = "INT_LITERAL"
    FLOAT_LITERAL  = "FLOAT_LITERAL"
    STRING_LITERAL = "STRING_LITERAL"
    BOOL_LITERAL   = "BOOL_LITERAL"

    PLUS    = "+"
    MINUS   = "-"
    STAR    = "*"
    SLASH   = "/"
    PERCENT = "%"

    EQ_EQ   = "=="
    BANG_EQ = "!="
    LT      = "<"
    LT_EQ   = "<="
    GT      = ">"
    GT_EQ   = ">="

    AMP_AMP  = "&&"
    PIPE_PIPE = "||"
    BANG     = "!"

    ASSIGN      = "="
    PLUS_ASSIGN = "+="
    MINUS_ASSIGN = "-="
    STAR_ASSIGN = "*="
    SLASH_ASSIGN = "/="

    LPAREN    = "("
    RPAREN    = ")"
    LBRACE    = "{"
    RBRACE    = "}"
    LBRACKET  = "["
    RBRACKET  = "]"
    SEMICOLON = ";"
    COMMA     = ","
    COLON     = ":"
    ARROW     = "->"

    EOF   = "EOF"
    ERROR = "ERROR"


KEYWORDS: Dict[str, TokenType] = {
    "if":     TokenType.KW_IF,
    "else":   TokenType.KW_ELSE,
    "while":  TokenType.KW_WHILE,
    "for":    TokenType.KW_FOR,
    "int":    TokenType.KW_INT,
    "float":  TokenType.KW_FLOAT,
    "bool":   TokenType.KW_BOOL,
    "return": TokenType.KW_RETURN,
    "true":   TokenType.KW_TRUE,
    "false":  TokenType.KW_FALSE,
    "void":   TokenType.KW_VOID,
    "struct": TokenType.KW_STRUCT,
    "fn":     TokenType.KW_FN,
    "null":   TokenType.KW_NULL,
}

TOKEN_NAMES: Dict[TokenType, str] = {
    TokenType.KW_IF:       "keyword 'if'",
    TokenType.KW_ELSE:     "keyword 'else'",
    TokenType.KW_WHILE:    "keyword 'while'",
    TokenType.KW_FOR:      "keyword 'for'",
    TokenType.KW_INT:      "keyword 'int'",
    TokenType.KW_FLOAT:    "keyword 'float'",
    TokenType.KW_BOOL:     "keyword 'bool'",
    TokenType.KW_RETURN:   "keyword 'return'",
    TokenType.KW_TRUE:     "keyword 'true'",
    TokenType.KW_FALSE:    "keyword 'false'",
    TokenType.KW_VOID:     "keyword 'void'",
    TokenType.KW_STRUCT:   "keyword 'struct'",
    TokenType.KW_FN:       "keyword 'fn'",
    TokenType.KW_NULL:     "keyword 'null'",
    TokenType.IDENTIFIER:  "identifier",
    TokenType.INT_LITERAL: "integer literal",
    TokenType.FLOAT_LITERAL: "float literal",
    TokenType.STRING_LITERAL: "string literal",
    TokenType.BOOL_LITERAL: "boolean literal",
    TokenType.SEMICOLON:   "';'",
    TokenType.LPAREN:      "'('",
    TokenType.RPAREN:      "')'",
    TokenType.LBRACE:      "'{'",
    TokenType.RBRACE:      "'}'",
    TokenType.LBRACKET:    "'['",
    TokenType.RBRACKET:    "']'",
    TokenType.COMMA:       "','",
    TokenType.COLON:       "':'",
    TokenType.ARROW:       "'->'",
    TokenType.EOF:         "end of file",
}


@dataclass
class Token:
    type:    TokenType
    lexeme:  str
    line:    int
    column:  int
    literal: Union[int, float, bool, str, None] = field(default=None)

    def __repr__(self) -> str:
        base = f"{self.line}:{self.column} {self.type.name} {self.lexeme!r}"
        if self.literal is not None:
            base += f" [{self.literal!r}]"
        return base

    def format_output(self) -> str:
        base = f"{self.line}:{self.column} {self.type.name} {self.lexeme!r}"
        if self.literal is not None:
            base += f" {self.literal!r}"
        return base
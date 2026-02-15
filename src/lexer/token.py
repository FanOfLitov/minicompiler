from enum import Enum, auto
from typing import Any, Union

class TokenType(Enum):
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

	IDENTIFIER = auto()
	INT_LITERAL = auto()
	FLOAT_LITERAL = auto()
	STRING_LITERAL = auto()
	BOOL_LITERAL = auto()

"""
Semantic analyzer Type System. Fully compatible with Python 3.8+.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Tuple, Set


class Type:
    def is_numeric(self) -> bool:
        return False

    def is_assignable_from(self, other: "Type") -> bool:
        return self == other

    def __eq__(self, other: object) -> bool:
        return type(self) is type(other)

    def __hash__(self) -> int:
        return hash(type(self))


class IntType(Type):
    def is_numeric(self) -> bool: return True
    def is_assignable_from(self, other: Type) -> bool:
        return isinstance(other, IntType)
    def __repr__(self) -> str: return "int"


class FloatType(Type):
    def is_numeric(self) -> bool: return True
    def is_assignable_from(self, other: Type) -> bool:
        return isinstance(other, (IntType, FloatType))
    def __repr__(self) -> str: return "float"


class BoolType(Type):
    def is_assignable_from(self, other: Type) -> bool:
        return isinstance(other, BoolType)
    def __repr__(self) -> str: return "bool"


class StringType(Type):
    def is_assignable_from(self, other: Type) -> bool:
        return isinstance(other, StringType)
    def __repr__(self) -> str: return "string"


class VoidType(Type):
    def __repr__(self) -> str: return "void"


class NullType(Type):
    def __repr__(self) -> str: return "null"


@dataclass(eq=False)
class StructType(Type):
    name:   str
    fields: Dict[str, Type] = field(default_factory=dict)

    def is_assignable_from(self, other: Type) -> bool:
        if isinstance(other, NullType):
            return True
        return isinstance(other, StructType) and other.name == self.name

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StructType) and self.name == other.name

    def __hash__(self) -> int:
        return hash(("struct", self.name))

    def __repr__(self) -> str:
        return f"struct {self.name}"


@dataclass(eq=False)
class FunctionType(Type):
    param_types: List[Type]
    return_type: Type

    def __eq__(self, other: object) -> bool:
        return (isinstance(other, FunctionType)
                and self.param_types == other.param_types
                and self.return_type == other.return_type)

    def __hash__(self) -> int:
        return hash(("fn", tuple(self.param_types), self.return_type))

    def __repr__(self) -> str:
        params = ", ".join(str(p) for p in self.param_types)
        return f"fn({params}) -> {self.return_type}"


INT    = IntType()
FLOAT  = FloatType()
BOOL   = BoolType()
STRING = StringType()
VOID   = VoidType()
NULL   = NullType()

BUILTIN_TYPES: Dict[str, Type] = {
    "int":    INT,
    "float":  FLOAT,
    "bool":   BOOL,
    "string": STRING,
    "void":   VOID,
}


def resolve_type(name: str, struct_registry: Dict[str, StructType]) -> Optional[Type]:
    if name in BUILTIN_TYPES:
        return BUILTIN_TYPES[name]
    return struct_registry.get(name)


_ARITHMETIC_OPS: Set[str] = {'+', '-', '*', '/', '%'}
_COMPARISON_OPS: Set[str] = {'==', '!=', '<', '<=', '>', '>='}
_LOGICAL_OPS: Set[str]    = {'&&', '||'}


def binary_result_type(op: str, left: Type, right: Type) -> Optional[Type]:
    if op in _ARITHMETIC_OPS:
        if left.is_numeric() and right.is_numeric():
            if isinstance(left, FloatType) or isinstance(right, FloatType):
                return FLOAT
            return INT
        return None

    if op in _COMPARISON_OPS:
        if op in {'==', '!='}:
            if type(left) is type(right):
                return BOOL
            if left.is_numeric() and right.is_numeric():
                return BOOL
            return None
        if left.is_numeric() and right.is_numeric():
            return BOOL
        return None

    if op in _LOGICAL_OPS:
        if isinstance(left, BoolType) and isinstance(right, BoolType):
            return BOOL
        return None

    return None


def unary_result_type(op: str, operand: Type) -> Optional[Type]:
    if op == '-':
        if isinstance(operand, IntType):
            return INT
        if isinstance(operand, FloatType):
            return FLOAT
    if op == '!':
        if isinstance(operand, BoolType):
            return BOOL
    return None
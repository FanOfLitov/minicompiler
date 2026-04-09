from dataclasses import dataclass
from typing import Dict, List, Optional

class Type:
    def __eq__(self, other):
        return isinstance(other, type(self)) and self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(str(self))

    def is_convertible_to(self, other: 'Type') -> bool:
        """Может ли текущий тип быть неявно преобразован в другой."""
        if self == other:
            return True
        # int -> float
        if isinstance(self, PrimitiveType) and self.name == 'int' and \
           isinstance(other, PrimitiveType) and other.name == 'float':
            return True
        return False

class PrimitiveType(Type):
    def __init__(self, name: str):
        self.name = name   # 'int', 'float', 'bool', 'void', 'string'

    def __str__(self):
        return self.name

    def __eq__(self, other):
        return isinstance(other, PrimitiveType) and self.name == other.name

class StructType(Type):
    def __init__(self, name: str, fields: Dict[str, Type]):
        self.name = name
        self.fields = fields   # имя поля -> тип

    def __str__(self):
        return f"struct {self.name}"

class FunctionType(Type):
    def __init__(self, param_types: List[Type], return_type: Type):
        self.param_types = param_types
        self.return_type = return_type

    def __str__(self):
        params = ', '.join(str(t) for t in self.param_types)
        return f"({params}) -> {self.return_type}"

class ArrayType(Type):
    def __init__(self, elem_type: Type, size: Optional[int] = None):
        self.elem_type = elem_type
        self.size = size   # None для динамических массивов

    def __str__(self):
        return f"[{self.size if self.size else ''}]{self.elem_type}"
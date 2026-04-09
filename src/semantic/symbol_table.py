from enum import Enum
from typing import Dict, Optional, List, Any
from .type_system import Type

class SymbolKind(Enum):
    VARIABLE = 1
    FUNCTION = 2
    PARAMETER = 3
    STRUCT = 4
    FIELD = 5

@dataclass
class SymbolInfo:
    name: str
    kind: SymbolKind
    type: Type
    line: int
    column: int
    # Для функций
    parameters: Optional[List['SymbolInfo']] = None
    # Для структур
    fields: Optional[Dict[str, Type]] = None

class SymbolTable:
    def __init__(self):
        self.scopes = [{}]          # список словарей: текущая область
        self.scope_names = ['global']  # имена областей для отладки

    def enter_scope(self, name: str = 'block'):
        self.scopes.append({})
        self.scope_names.append(name)

    def exit_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()
            self.scope_names.pop()

    def insert(self, symbol: SymbolInfo) -> bool:
        """Вставить символ в текущую область. Возвращает False, если уже существует."""
        current = self.scopes[-1]
        if symbol.name in current:
            return False
        current[symbol.name] = symbol
        return True

    def lookup(self, name: str) -> Optional[SymbolInfo]:
        """Поиск во всех видимых областях (от внутренней к глобальной)."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    def lookup_local(self, name: str) -> Optional[SymbolInfo]:
        """Поиск только в текущей области."""
        return self.scopes[-1].get(name)

    def get_current_scope(self) -> Dict[str, SymbolInfo]:
        return self.scopes[-1]

    def dump(self) -> str:
        lines = []
        for i, scope in enumerate(self.scopes):
            lines.append(f"Scope {i}: {self.scope_names[i]}")
            for name, sym in scope.items():
                lines.append(f"  {name}: {sym.kind.name} : {sym.type}")
        return '\n'.join(lines)
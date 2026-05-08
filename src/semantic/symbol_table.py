"""
Hierarchical Scope and Symbol Table for Python 3.8+.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional


class SymbolKind:
    VARIABLE  = "variable"
    PARAMETER = "parameter"
    FUNCTION  = "function"
    STRUCT    = "struct"


@dataclass
class Symbol:
    name:         str
    kind:         str
    type:         "Type"  # Forward reference string
    decl_line:    int
    decl_column:  int
    stack_offset: Optional[int] = None
    is_initialized: bool = False


@dataclass
class Scope:
    name:    str
    parent:  Optional["Scope"]
    symbols: Dict[str, Symbol] = field(default_factory=dict)

    def define(self, symbol: Symbol) -> bool:
        if symbol.name in self.symbols:
            return False
        self.symbols[symbol.name] = symbol
        return True

    def lookup_local(self, name: str) -> Optional[Symbol]:
        return self.symbols.get(name)

    def lookup(self, name: str) -> Optional[Symbol]:
        scope: Optional[Scope] = self
        while scope is not None:
            sym = scope.symbols.get(name)
            if sym is not None:
                return sym
            scope = scope.parent
        return None

    def dump(self, indent: int = 0) -> str:
        lines = ["  " * indent + f"Scope({self.name}):"]
        for sym in self.symbols.values():
            lines.append(
                "  " * (indent + 1)
                + f"{sym.kind} {sym.name}: {sym.type}"
                + f" (declared at {sym.decl_line}:{sym.decl_column})"
            )
        return '\n'.join(lines)


class SymbolTable:
    def __init__(self) -> None:
        self._global = Scope("global", parent=None)
        self._stack: List[Scope] = [self._global]

    def enter_scope(self, name: str = "") -> Scope:
        label = name or f"block@{id(self)}"
        scope = Scope(label, parent=self.current_scope)
        self._stack.append(scope)
        return scope

    def exit_scope(self) -> Scope:
        if len(self._stack) == 1:
            raise RuntimeError("Cannot exit global scope")
        return self._stack.pop()

    @property
    def current_scope(self) -> Scope:
        return self._stack[-1]

    @property
    def global_scope(self) -> Scope:
        return self._global

    def depth(self) -> int:
        return len(self._stack)

    def define(self, symbol: Symbol) -> bool:
        return self.current_scope.define(symbol)

    def lookup(self, name: str) -> Optional[Symbol]:
        return self.current_scope.lookup(name)

    def lookup_local(self, name: str) -> Optional[Symbol]:
        return self.current_scope.lookup_local(name)

    def lookup_global(self, name: str) -> Optional[Symbol]:
        return self._global.lookup_local(name)

    def dump(self) -> str:
        return self._global.dump(0)
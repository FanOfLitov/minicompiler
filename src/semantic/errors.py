@dataclass
class SemanticError:
    message: str
    line: int
    column: int
    category: str   # 'undeclared', 'type_mismatch', 'duplicate', etc.

    def __str__(self):
        return f"{self.category}: {self.message} at {self.line}:{self.column}"
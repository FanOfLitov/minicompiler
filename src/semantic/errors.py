"""
Semantic error definitions and the error collector.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SemanticError:
    """A single semantic diagnostic with source location."""
    message:  str
    filename: str
    line:     int
    column:   int
    context:  str = ""          # e.g. "in function 'foo'"
    hint:     str = ""          # optional suggestion

    def format(self, source_lines: Optional[List[str]] = None) -> str:
        """
        Render in the style:
            semantic error: <message>
              --> file:line:col
              |
              |     <source line>
              |     ^
              = note: <hint>
        """
        parts = [f"semantic error: {self.message}"]
        parts.append(f"  --> {self.filename}:{self.line}:{self.column}")

        if self.context:
            parts.append(f"  | ({self.context})")

        if source_lines and 1 <= self.line <= len(source_lines):
            src_line = source_lines[self.line - 1]
            parts.append("  |")
            parts.append(f"  | {src_line}")
            pointer = " " * (self.column - 1) + "^"
            parts.append(f"  | {pointer}")
            parts.append("  |")

        if self.hint:
            parts.append(f"  = note: {self.hint}")

        return '\n'.join(parts)

    def __str__(self) -> str:
        base = (f"semantic error at {self.filename}:{self.line}:{self.column}"
                f": {self.message}")
        if self.hint:
            base += f"\n  note: {self.hint}"
        return base


class ErrorReporter:
    """Collects semantic errors; allows analysis to continue after errors."""

    def __init__(self, filename: str = "<unknown>",
                 source: str = "") -> None:
        self._filename     = filename
        self._source_lines = source.splitlines() if source else []
        self._errors: List[SemanticError] = []

    def error(self, message: str, line: int, column: int,
              context: str = "", hint: str = "") -> None:
        self._errors.append(SemanticError(
            message=message,
            filename=self._filename,
            line=line,
            column=column,
            context=context,
            hint=hint,
        ))

    @property
    def errors(self) -> List[SemanticError]:
        return list(self._errors)

    @property
    def has_errors(self) -> bool:
        return bool(self._errors)

    def format_all(self) -> str:
        return '\n\n'.join(
            e.format(self._source_lines) for e in self._errors
        )

    def summary(self) -> str:
        n = len(self._errors)
        if n == 0:
            return "No semantic errors."
        return (f"{n} semantic error{'s' if n != 1 else ''} found.")
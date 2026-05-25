"""
Sprint 7: external function call support.
Compatible with Python 3.8+.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Sequence


class ExternalCallError(ValueError):
    pass


@dataclass
class ExternalFunction:
    name: str
    return_type: str
    parameter_types: List[str] = field(default_factory=list)
    variadic: bool = False

    def validate_call(self, argument_types: Sequence[str]):
        if not self.variadic and len(argument_types) != len(self.parameter_types):
            raise ExternalCallError(
                "external function '{}' expects {} arguments, got {}".format(
                    self.name, len(self.parameter_types), len(argument_types)
                )
            )

        if self.variadic and len(argument_types) < len(self.parameter_types):
            raise ExternalCallError(
                "external function '{}' expects at least {} arguments, got {}".format(
                    self.name, len(self.parameter_types), len(argument_types)
                )
            )

        for index, expected in enumerate(self.parameter_types):
            actual = argument_types[index]

            if expected == actual:
                continue

            if expected == "float" and actual == "int":
                continue

            raise ExternalCallError(
                "argument {} to external function '{}': expected {}, got {}".format(
                    index + 1, self.name, expected, actual
                )
            )

    def declaration_line(self):
        args = ", ".join(self.parameter_types)
        if self.variadic:
            args = args + ", ..." if args else "..."
        return "extern {} {}({});".format(self.return_type, self.name, args)


class ExternalFunctionRegistry:
    def __init__(self):
        self._functions: Dict[str, ExternalFunction] = {}

    def register(self, fn: ExternalFunction):
        if fn.name in self._functions:
            raise ExternalCallError("external function '{}' is already registered".format(fn.name))
        self._functions[fn.name] = fn

    def get(self, name):
        if name not in self._functions:
            raise ExternalCallError("unknown external function '{}'".format(name))
        return self._functions[name]

    def validate_call(self, name, argument_types):
        fn = self.get(name)
        fn.validate_call(argument_types)
        return fn

    def names(self):
        return sorted(self._functions.keys())


def default_registry():
    registry = ExternalFunctionRegistry()

    registry.register(ExternalFunction("printf", "int", ["string"], variadic=True))
    registry.register(ExternalFunction("puts", "int", ["string"]))
    registry.register(ExternalFunction("getchar", "int", []))
    registry.register(ExternalFunction("malloc", "int", ["int"]))
    registry.register(ExternalFunction("free", "void", ["int"]))
    registry.register(ExternalFunction("memcpy", "int", ["int", "int", "int"]))
    registry.register(ExternalFunction("strlen", "int", ["string"]))

    return registry

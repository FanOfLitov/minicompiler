from pathlib import Path

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.ir.ir_generator import IRGenerator
from src.ssa.ssa_builder import SSABuilder


VALID_DIR = Path("tests/ssa/valid")

CASES = [
    "01_assignment_versions.src",
    "02_arithmetic.src",
    "03_function_call.src",
    "04_return_constant.src",
    "05_multiple_variables.src",
    "06_if_shape.src",
    "07_while_shape.src",
]


def build_ssa(src_path: Path) -> str:
    source = src_path.read_text(encoding="utf-8")

    scanner = Scanner(source, filename=str(src_path))
    tokens = scanner.scan_tokens() if hasattr(scanner, "scan_tokens") else scanner.scan_all()

    if scanner.errors:
        raise RuntimeError("\n".join(map(str, scanner.errors)))

    parser = Parser(tokens)
    ast = parser.parse()

    if ast is None or parser.errors:
        raise RuntimeError("\n".join(map(str, parser.errors)))

    analyzer = SemanticAnalyzer(filename=src_path.name, source=source)

    if not analyzer.analyze(ast):
        raise RuntimeError(analyzer.format_errors())

    ir = IRGenerator().generate(ast)
    ssa = SSABuilder().build(ir)

    return ssa.dump().strip() + "\n"


def main() -> None:
    for case in CASES:
        src_path = VALID_DIR / case
        expected_path = src_path.with_suffix(".expected")

        actual = build_ssa(src_path)
        expected_path.write_text(actual, encoding="utf-8")

        print(f"updated {expected_path}")


if __name__ == "__main__":
    main()

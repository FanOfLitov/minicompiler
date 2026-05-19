# src/cli.py
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _read_source(path: str) -> str:
    return Path(path).read_text(encoding="utf-8")


def _write_or_print(text: str, output_file: str | None) -> None:
    if output_file:
        Path(output_file).write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")
    else:
        print(text)


def _scan_source(source: str, filename: str):
    from src.lexer.scanner import Scanner

    scanner = Scanner(source, filename=filename)
    tokens = scanner.scan_tokens() if hasattr(scanner, "scan_tokens") else scanner.scan_all()
    return scanner, tokens


def _parse_source(source: str, filename: str):
    from src.parser.parser import Parser

    scanner, tokens = _scan_source(source, filename)
    if scanner.errors:
        raise SystemExit("Lexical errors found:\n" + "\n".join(str(e) for e in scanner.errors))

    parser = Parser(tokens)
    ast = parser.parse()
    if parser.errors:
        raise SystemExit("Parse errors found:\n" + "\n".join(str(e) for e in parser.errors))
    if ast is None:
        raise SystemExit("Parse failed: parser returned None")
    return ast


def lex_command(args: argparse.Namespace) -> int:
    source = _read_source(args.input)
    scanner, tokens = _scan_source(source, args.input)

    # format_output есть в Token; fallback на str/repr, если метод изменят.
    lines = []
    for token in tokens:
        if hasattr(token, "format_output"):
            lines.append(token.format_output())
        else:
            lines.append(str(token))

    if scanner.errors:
        lines.append("")
        lines.append("Lexical errors:")
        lines.extend(str(e) for e in scanner.errors)

    _write_or_print("\n".join(lines), args.output)
    return 1 if scanner.errors else 0


def parse_command(args: argparse.Namespace) -> int:
    source = _read_source(args.input)
    ast = _parse_source(source, args.input)

    if args.format == "text":
        from src.parser.ast_printer import TextPrinter
        text = TextPrinter().print(ast)
    elif args.format == "dot":
        from src.parser.ast_printer import DotPrinter
        text = DotPrinter().generate(ast)
    elif args.format == "json":
        from src.parser.ast_printer import JsonPrinter
        text = JsonPrinter().serialise(ast)
    else:
        raise SystemExit(f"Unknown format: {args.format}")

    _write_or_print(text, args.output)
    return 0


def semantic_command(args: argparse.Namespace) -> int:
    source = _read_source(args.input)
    ast = _parse_source(source, args.input)

    from src.semantic.analyzer import SemanticAnalyzer
    from src.parser.ast_printer import TextPrinter

    analyzer = SemanticAnalyzer(filename=args.input, source=source)
    ok = analyzer.analyze(ast)

    parts: list[str] = []
    if args.symbols:
        parts.append("Symbol table:")
        parts.append(analyzer.symbol_table.dump())
        parts.append("")

    if ok:
        parts.append("Semantic analysis passed.")
        if args.ast:
            parts.append("")
            parts.append(TextPrinter().print(ast))
    else:
        parts.append(analyzer.format_errors())
        parts.append(analyzer.summary())

    _write_or_print("\n".join(parts), args.output)
    return 0 if ok else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="minicc", description="MiniCompiler CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    lex = sub.add_parser("lex", help="Tokenize source file")
    lex.add_argument("-i", "--input", required=True)
    lex.add_argument("-o", "--output")
    lex.set_defaults(func=lex_command)

    parse = sub.add_parser("parse", help="Parse source file and print AST")
    parse.add_argument("-i", "--input", required=True)
    parse.add_argument("-o", "--output")
    parse.add_argument("-f", "--format", choices=("text", "dot", "json"), default="text")
    parse.set_defaults(func=parse_command)

    sem = sub.add_parser("semantic", help="Run semantic analysis")
    sem.add_argument("-i", "--input", required=True)
    sem.add_argument("-o", "--output")
    sem.add_argument("--symbols", action="store_true", help="Print symbol table")
    sem.add_argument("--ast", action="store_true", help="Print decorated AST when analysis succeeds")
    sem.set_defaults(func=semantic_command)

    # Алиасы под твой run.py: check = semantic
    check = sub.add_parser("check", help="Alias for semantic")
    check.add_argument("-i", "--input", required=True)
    check.add_argument("-o", "--output")
    check.add_argument("--symbols", action="store_true")
    check.add_argument("--ast", action="store_true")
    check.add_argument("-v", "--verbose", action="store_true")
    check.set_defaults(func=semantic_command)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

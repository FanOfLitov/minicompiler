#!/usr/bin/env python3
"""
MiniCompiler – command-line entry point.

Usage examples:
    ./main.py lex   --input examples/hello.src
    ./main.py parse --input examples/hello.src --format dot
    ./main.py check --input examples/hello.src --verbose
    ./main.py compile --input examples/hello.src   (full pipeline)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from src.lexer  import Scanner
from src.parser import Parser, TextPrinter, DotPrinter, JsonPrinter
from src.semantic import SemanticAnalyzer


# ══════════════════════════════════════════════════════════════════════════════
#  Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _read_file(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except FileNotFoundError:
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    except IOError as e:
        print(f"error reading {path}: {e}", file=sys.stderr)
        sys.exit(1)


def _write_output(content: str, output_path: Optional[str]) -> None:
    if output_path:
        Path(output_path).write_text(content, encoding="utf-8")
        print(f"Output written to {output_path}")
    else:
        print(content)


# ══════════════════════════════════════════════════════════════════════════════
#  Pipeline stages
# ══════════════════════════════════════════════════════════════════════════════

def run_lex(args: argparse.Namespace) -> int:
    source  = _read_file(args.input)
    scanner = Scanner(source, filename=args.input)
    tokens  = scanner.scan_all()

    # Report lexer errors
    for err in scanner.errors:
        print(err, file=sys.stderr)

    lines = [t.format_output() for t in tokens]
    _write_output('\n'.join(lines), getattr(args, 'output', None))

    return 1 if scanner.errors else 0


def run_parse(args: argparse.Namespace) -> int:
    source  = _read_file(args.input)
    scanner = Scanner(source, filename=args.input)
    tokens  = scanner.scan_all()

    for err in scanner.errors:
        print(err, file=sys.stderr)

    parser  = Parser(tokens)
    program = parser.parse()

    for err in parser.errors:
        print(err, file=sys.stderr)

    if program is None:
        print("Parsing failed.", file=sys.stderr)
        return 1

    fmt = getattr(args, 'format', 'text')
    if fmt == 'dot':
        output = DotPrinter().generate(program)
    elif fmt == 'json':
        output = JsonPrinter().serialise(program)
    else:
        output = TextPrinter().print(program)

    _write_output(output, getattr(args, 'output', None))
    return 1 if (scanner.errors or parser.errors) else 0


def run_check(args: argparse.Namespace) -> int:
    source  = _read_file(args.input)
    scanner = Scanner(source, filename=args.input)
    tokens  = scanner.scan_all()

    for err in scanner.errors:
        print(err, file=sys.stderr)

    parser  = Parser(tokens)
    program = parser.parse()

    for err in parser.errors:
        print(err, file=sys.stderr)

    if program is None:
        print("Cannot perform semantic analysis: parse failed.",
              file=sys.stderr)
        return 1

    analyser = SemanticAnalyzer(filename=args.input, source=source)
    ok       = analyser.analyze(program)

    if analyser.has_errors:
        print(analyser.format_errors(), file=sys.stderr)
    else:
        print("Semantic analysis passed – no errors.")

    if getattr(args, 'verbose', False):
        print("\n─── Symbol Table ───")
        print(analyser.symbol_table.dump())
        print("\n─── Decorated AST ──")
        print(TextPrinter().print(program))

    print(analyser.summary())
    return 0 if ok else 1


def run_compile(args: argparse.Namespace) -> int:
    """Run all three stages and report results."""
    print("=== Lexer ===")
    source  = _read_file(args.input)
    scanner = Scanner(source, filename=args.input)
    tokens  = scanner.scan_all()

    lex_ok = not scanner.errors
    print(f"Tokens: {len(tokens)}  Errors: {len(scanner.errors)}")
    for e in scanner.errors:
        print(f"  {e}", file=sys.stderr)

    print("\n=== Parser ===")
    parser  = Parser(tokens)
    program = parser.parse()
    par_ok  = program is not None and not parser.errors
    print(f"Errors: {len(parser.errors)}")
    for e in parser.errors:
        print(f"  {e}", file=sys.stderr)

    if program is None:
        print("Cannot continue.", file=sys.stderr)
        return 1

    print("\n=== Semantic Analysis ===")
    analyser = SemanticAnalyzer(filename=args.input, source=source)
    sem_ok   = analyser.analyze(program)
    print(analyser.summary())
    if not sem_ok:
        print(analyser.format_errors(), file=sys.stderr)

    overall = lex_ok and par_ok and sem_ok
    print(f"\n{'✓ Compilation successful' if overall else '✗ Compilation failed'}")
    return 0 if overall else 1


# ══════════════════════════════════════════════════════════════════════════════
#  CLI setup
# ══════════════════════════════════════════════════════════════════════════════

def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        prog="minicc",
        description="MiniCompiler – a teaching compiler for a C-like language.",
    )
    sub = root.add_subparsers(dest="command", required=True)

    # ── lex ──────────────────────────────────────────────────────────────
    p_lex = sub.add_parser("lex", help="Tokenise source file and print tokens")
    p_lex.add_argument("--input",  "-i", required=True, help="Source file")
    p_lex.add_argument("--output", "-o", help="Output file (default: stdout)")

    # ── parse ─────────────────────────────────────────────────────────────
    p_parse = sub.add_parser("parse", help="Parse and dump the AST")
    p_parse.add_argument("--input",  "-i", required=True)
    p_parse.add_argument("--output", "-o")
    p_parse.add_argument(
        "--format", "-f",
        choices=["text", "dot", "json"],
        default="text",
        help="AST output format (default: text)",
    )

    # ── check ─────────────────────────────────────────────────────────────
    p_check = sub.add_parser("check", help="Run semantic analysis")
    p_check.add_argument("--input",   "-i", required=True)
    p_check.add_argument("--verbose", "-v", action="store_true")

    # ── compile ───────────────────────────────────────────────────────────
    p_comp = sub.add_parser("compile", help="Run full pipeline")
    p_comp.add_argument("--input", "-i", required=True)
    p_comp.add_argument("--output", "-o")

    return root


def main() -> int:
    args = build_parser().parse_args()
    dispatch = {
        "lex":     run_lex,
        "parse":   run_parse,
        "check":   run_check,
        "compile": run_compile,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
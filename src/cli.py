# src/cli.py
import sys


def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.cli {lex|parse|semantic|check|ir} ...")
        print("  For help: python -m src.cli --help")
        sys.exit(1)

    command = sys.argv[1]

    if command == "lex":
        lex_command()
    elif command == "parse":
        parse_command()
    elif command in ("semantic", "check"):
        semantic_command()
    elif command == "ir":
        ir_command()
    elif command in ("--help", "-h"):
        show_help()
    else:
        print(f"Unknown command: {command}")
        show_help()
        sys.exit(1)


def show_help():
    print("MiniCompiler - Command Line Interface")
    print()
    print("Commands:")
    print("  lex --input FILE [--output FILE]")
    print("      Tokenize source file and print tokens.")
    print()
    print("  parse --input FILE [--output FILE] [--format {text|dot|json}]")
    print("      Parse source file and output AST in specified format.")
    print()
    print("  semantic --input FILE [--output FILE] [--symbols]")
    print("  check --input FILE [--output FILE] [--symbols]")
    print("      Run semantic analysis.")
    print()
    print("  ir --input FILE [--output FILE] [--format {text|dot}]")
    print("      Generate intermediate representation from source file.")
    print()
    print("Options:")
    print("  --input, -i FILE       Input source file")
    print("  --output, -o FILE      Output file")
    print("  --format, -f FORMAT    Output format")
    print("  --help, -h             Show this help message")


def _read_source(input_file):
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)


def _write_or_print(text, output_file=None, success_message=None):
    if output_file:
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
                if not text.endswith("\n"):
                    f.write("\n")
            if success_message:
                print(success_message)
        except Exception as e:
            print(f"Error writing output: {e}")
            sys.exit(1)
    else:
        print(text)


def _scan_source(source, filename="<unknown>"):
    from src.lexer.scanner import Scanner

    scanner = Scanner(source, filename=filename)
    if hasattr(scanner, "scan_tokens"):
        tokens = scanner.scan_tokens()
    else:
        tokens = scanner.scan_all()

    if scanner.errors:
        print("\n".join(map(str, scanner.errors)))
        sys.exit(1)

    if any(token.type.name == "ERROR" for token in tokens):
        print("Lexical errors found.")
        sys.exit(1)

    return tokens


def _parse_source(source, filename="<unknown>"):
    from src.parser.parser import Parser

    tokens = _scan_source(source, filename)
    parser = Parser(tokens)
    ast = parser.parse()

    if ast is None or parser.errors:
        if parser.errors:
            print("\n".join(map(str, parser.errors)))
        else:
            print("Parse error: parser returned no AST.")
        sys.exit(1)

    return ast


def _semantic_check(source, filename="<unknown>"):
    from src.semantic.analyzer import SemanticAnalyzer

    ast = _parse_source(source, filename)
    analyzer = SemanticAnalyzer(filename=filename, source=source)
    ok = analyzer.analyze(ast)

    if not ok:
        print(analyzer.format_errors())
        sys.exit(1)

    return ast, analyzer


def lex_command():
    input_file = None
    output_file = None

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ("--input", "-i") and i + 1 < len(sys.argv):
            input_file = sys.argv[i + 1]
            i += 2
        elif arg in ("--output", "-o") and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        else:
            print(f"Unknown argument for lex: {arg}")
            sys.exit(1)

    if not input_file:
        print("Error: No input file specified. Use --input <file>")
        sys.exit(1)

    source = _read_source(input_file)

    from src.lexer.scanner import Scanner

    scanner = Scanner(source, filename=input_file)
    tokens = scanner.scan_tokens() if hasattr(scanner, "scan_tokens") else scanner.scan_all()

    if scanner.errors:
        output_text = "\n".join(map(str, scanner.errors))
    else:
        output_text = "\n".join(str(token) for token in tokens)

    _write_or_print(
        output_text,
        output_file,
        success_message=f"Tokens written to {output_file}" if output_file else None,
    )


def parse_command():
    input_file = None
    output_file = None
    fmt = "text"

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ("--input", "-i") and i + 1 < len(sys.argv):
            input_file = sys.argv[i + 1]
            i += 2
        elif arg in ("--output", "-o") and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif arg in ("--format", "-f") and i + 1 < len(sys.argv):
            fmt = sys.argv[i + 1].lower()
            i += 2
        else:
            print(f"Unknown argument for parse: {arg}")
            sys.exit(1)

    if not input_file:
        print("Error: No input file specified. Use --input <file>")
        sys.exit(1)

    if fmt not in ("text", "dot", "json"):
        print(f"Error: Unknown format '{fmt}'. Supported formats: text, dot, json")
        sys.exit(1)

    source = _read_source(input_file)
    ast = _parse_source(source, input_file)

    if fmt == "text":
        from src.parser.ast_printer import TextPrinter, ASTPrinter

        if "TextPrinter" in globals():
            output_text = TextPrinter().print(ast)
        else:
            # Fallback for older ast_printer.py
            import io
            buf = io.StringIO()
            ASTPrinter().print_text(ast, buf)
            output_text = buf.getvalue()

    elif fmt == "dot":
        from src.parser.ast_printer import DotPrinter

        output_text = DotPrinter().generate(ast)

    else:
        from src.parser.ast_printer import JsonPrinter

        printer = JsonPrinter()
        if hasattr(printer, "print"):
            output_text = printer.print(ast)
        elif hasattr(printer, "generate"):
            output_text = printer.generate(ast)
        else:
            print("JSON output is not supported by current JsonPrinter.")
            sys.exit(1)

    _write_or_print(
        output_text,
        output_file,
        success_message=f"AST written to {output_file}" if output_file else None,
    )


def semantic_command():
    input_file = None
    output_file = None
    show_symbols = False

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ("--input", "-i") and i + 1 < len(sys.argv):
            input_file = sys.argv[i + 1]
            i += 2
        elif arg in ("--output", "-o") and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif arg == "--symbols":
            show_symbols = True
            i += 1
        else:
            print(f"Unknown argument for semantic: {arg}")
            sys.exit(1)

    if not input_file:
        print("Error: No input file specified. Use --input <file>")
        sys.exit(1)

    source = _read_source(input_file)
    ast, analyzer = _semantic_check(source, input_file)

    lines = ["Semantic analysis passed."]

    if show_symbols:
        lines.append("")
        lines.append("Symbol table:")
        lines.append(analyzer.symbol_table.dump())

    output_text = "\n".join(lines)

    _write_or_print(
        output_text,
        output_file,
        success_message=f"Semantic report written to {output_file}" if output_file else None,
    )


def ir_command():
    input_file = None
    output_file = None
    fmt = "text"

    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg in ("--input", "-i") and i + 1 < len(sys.argv):
            input_file = sys.argv[i + 1]
            i += 2
        elif arg in ("--output", "-o") and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        elif arg in ("--format", "-f") and i + 1 < len(sys.argv):
            fmt = sys.argv[i + 1].lower()
            i += 2
        else:
            print(f"Unknown argument for ir: {arg}")
            sys.exit(1)

    if not input_file:
        print("Error: No input file specified. Use --input <file>")
        sys.exit(1)

    if fmt not in ("text", "dot"):
        print(f"Error: Unknown IR format '{fmt}'. Supported formats: text, dot")
        sys.exit(1)

    source = _read_source(input_file)
    ast, _analyzer = _semantic_check(source, input_file)

    from src.ir.ir_generator import IRGenerator
    from src.ir.control_flow import function_to_dot

    generator = IRGenerator()
    program = generator.generate(ast)

    if fmt == "text":
        output_text = program.dump()
    else:
        if not program.functions:
            output_text = "digraph empty_cfg {\n}"
        else:
            first_function = next(iter(program.functions.values()))
            output_text = function_to_dot(first_function)

    _write_or_print(
        output_text,
        output_file,
        success_message=f"IR written to {output_file}" if output_file else None,
    )


if __name__ == "__main__":
    main()

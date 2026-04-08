# src/cli.py
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python -m src.cli {lex|parse} ...")
        print("  For help: python -m src.cli --help")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'lex':
        lex_command()
    elif command == 'parse':
        parse_command()
    elif command in ('--help', '-h'):
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
    print("      Parse source file and output AST in specified format (default: text).")
    print()
    print("Options:")
    print("  --help, -h      Show this help message.")

def lex_command():
    input_file = None
    output_file = None
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--input' and i+1 < len(sys.argv):
            input_file = sys.argv[i+1]
            i += 2
        elif arg == '--output' and i+1 < len(sys.argv):
            output_file = sys.argv[i+1]
            i += 2
        else:
            print(f"Unknown argument for lex: {arg}")
            sys.exit(1)

    if not input_file:
        print("Error: No input file specified. Use --input <file>")
        sys.exit(1)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    from src.lexer.scanner import Scanner
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    output_lines = [str(token) for token in tokens]
    output_text = '\n'.join(output_lines)

    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output_text + '\n')
            print(f"Tokens written to {output_file}")
        except Exception as e:
            print(f"Error writing output: {e}")
            sys.exit(1)
    else:
        print(output_text)

def parse_command():
    input_file = None
    output_file = None
    format = 'text'
    i = 2
    while i < len(sys.argv):
        arg = sys.argv[i]
        if arg == '--input' and i+1 < len(sys.argv):
            input_file = sys.argv[i+1]
            i += 2
        elif arg == '--output' and i+1 < len(sys.argv):
            output_file = sys.argv[i+1]
            i += 2
        elif arg == '--format' and i+1 < len(sys.argv):
            format = sys.argv[i+1].lower()
            i += 2
        else:
            print(f"Unknown argument for parse: {arg}")
            sys.exit(1)

    if not input_file:
        print("Error: No input file specified. Use --input <file>")
        sys.exit(1)

    if format not in ('text', 'dot', 'json'):
        print(f"Error: Unknown format '{format}'. Supported formats: text, dot, json")
        sys.exit(1)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    from src.lexer.scanner import Scanner
    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    if any(token.type.name == 'ERROR' for token in tokens):
        print("Lexical errors found. Cannot parse.")
        sys.exit(1)

    from src.parser.parser import Parser
    parser = Parser(tokens)
    try:
        ast = parser.parse()
    except Exception as e:
        print(f"Parse error: {e}")
        sys.exit(1)

    if output_file:
        out = open(output_file, 'w', encoding='utf-8')
    else:
        out = sys.stdout

    if format == 'text':
        from src.parser.ast_printer import ASTPrinter
        printer = ASTPrinter()
        printer.print_text(ast, out)
    elif format == 'dot':
        from src.parser.ast_printer import ASTDotPrinter
        printer = ASTDotPrinter()
        printer.print_dot(ast, out)
    elif format == 'json':
        print("JSON output not implemented yet.", file=sys.stderr)
        sys.exit(1)

    if output_file:
        out.close()
        print(f"AST written to {output_file}")

if __name__ == '__main__':
    main()
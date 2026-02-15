import sys
from src.lexer.scanner import Scanner

def main():
    if len(sys.argv) < 3 or sys.argv[1] != 'lex':
        print("Usage: python -m src.cli lex --input <file> [--output <file>]")
        sys.exit(1)

    input_file = None
    output_file = None
    i = 2
    while i < len(sys.argv):
        if sys.argv[i] == '--input' and i + 1 < len(sys.argv):
            input_file = sys.argv[i + 1]
            i += 2
        elif sys.argv[i] == '--output' and i + 1 < len(sys.argv):
            output_file = sys.argv[i + 1]
            i += 2
        else:
            print(f"Unknown argument: {sys.argv[i]}")
            i += 1

    if not input_file:
        print("Error: No input file specified")
        sys.exit(1)

    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        sys.exit(1)

    scanner = Scanner(source)
    tokens = scanner.scan_tokens()

    output = '\n'.join(str(token) for token in tokens)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output + '\n')
        print(f"Tokens written to {output_file}")
    else:
        print(output)


if __name__ == '__main__':
    main()
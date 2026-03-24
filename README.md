Ваня Б
 
Спринт 1: токенизация (lexical analysis).

## Сборка и запуск
Проект будет написан на Python 3.10+ 
Для установки зависимостей:
pip install -e .

# MiniCompiler - Sprint 1: Lexical Analysis

A simple compiler for a C-like language, implementing lexical analysis (tokenization).

## Project Structure

minicompiler/
├── src/ # Source code
│ ├── cli.py # Command-line interface
│ ├── lexer/ # Lexical analysis module (Sprint 1)
│ │ ├── scanner.py
│ │ ├── token.py
│ │ └── init.py
│ ├── parser/ # Syntax analysis module (Sprint 2)
│ │ ├── parser.py
│ │ ├── ast.py
│ │ ├── ast_printer.py
│ │ └── grammar.txt
│ └── utils/ # (future)
├── tests/ # Test suite
│ ├── lexer/ # Lexer tests
│ │ ├── valid/
│ │ └── invalid/
│ └── parser/ # Parser tests (Sprint 2)
│ ├── valid/
│ │ ├── expressions/
│ │ ├── statements/
│ │ └── full_programs/
│ └── invalid/
│ └── syntax_errors/
├── examples/ # Example source files
├── test_runner.py # Test runner for lexer
├── test_parser.py # Test runner for parser (Sprint 2)
├── run.py # Unified command runner
├── Makefile # Build automation
└── README.md



## Language Features (Sprint 1)

### Lexical Elements
- **Keywords**: `if`, `else`, `while`, `for`, `int`, `float`, `bool`, `return`, `true`, `false`, `void`, `struct`, `fn`
- **Identifiers**: Start with letter/underscore, followed by letters/digits/underscores
- **Literals**: 
  - Integers: `42`, `-100`, `0`
  - Floats: `3.14`, `0.5`, `.25`
  - Strings: `"Hello, World!"`
- **Operators**: `+ - * / % = == != < <= > >= && || ! += -= *= /=`
- **Delimiters**: `( ) { } [ ] ; , : .`
- **Comments**: `// single-line` and `/* multi-line */`

## Installation & Usage

### Quick Start
# Clone the repository
git clone ithub.com/FanOfLitov/minicompiler
cd minicompiler

# Run lexer on example file
python -m src.cli lex --input examples/hello.src

# Or using the test runner
python test_runner.py

Using Makefile

# Run all tests
make test

# Run with verbose output
make test-verbose

# Generate expected output files
make test-generate

# Clean generated files
make clean

# Show help
make help

Command Line Interface

# Basic usage
python -m src.cli lex --input <source_file>

# With output file
python -m src.cli lex --input <source_file> --output <tokens_file>

# Example
python -m src.cli lex --input examples/hello.src --output tokens.txt

Testing

The project includes comprehensive test coverage:
Test Categories

    Valid Tests (15 files): Test correct tokenization
        Identifiers, keywords, literals
        Operators and delimiters
        Comments and whitespace
        Complex expressions

    Invalid Tests (10 files): Test error handling
        Invalid characters
        Unterminated strings/comments
        Malformed numbers
        Syntax errors

Running Tests


# Run all tests
python test_runner.py

# Run specific test
python test_runner.py --test tests/lexer/valid/01_simple_identifiers.src

# Generate expected output (for new tests)
python test_runner.py --generate

Token Output Format

Tokens are printed in the following format:

LINE:COLUMN TOKEN_TYPE "LEXEME" [LITERAL_VALUE]

Example:

1:1 KW_FN "fn"
1:4 IDENTIFIER "main"
1:8 LPAREN "("
1:9 RPAREN ")"
1:10 LBRACE "{"
2:5 KW_INT "int"
2:9 IDENTIFIER "counter"
2:16 ASSIGN "="
2:18 INT_LITERAL "42" 42
2:20 SEMICOLON ";"
3:1 RBRACE "}"
4:1 END_OF_FILE ""

=
Adding New Tests

    Add source file to tests/lexer/valid/ or tests/lexer/invalid/
    For valid tests, generate expected output: python test_runner.py --generate

    Run tests to verify: python test_runner.py

Extending the Lexer

    Add new token type to src/lexer/token.py
    Update scanner logic in src/lexer/scanner.py
    Add corresponding tests
    Run test suite

Sprint 1 Deliverables 

    Project repository with clean structure
    Formal language specification (lexical elements)
    Working lexer/scanner
    Comprehensive test suite (25+ test cases)
    Build automation (Makefile)
    Command-line interface
    Error handling with position tracking

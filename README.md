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

Unified Runner (run.py)

python run.py lex --input FILE [--output FILE] – tokenize

python run.py parse --input FILE [--output FILE] [--format text|dot] – parse and output AST

python run.py test – run all lexer tests

python run.py test-parser – run all parser tests

python run.py generate – generate expected output files (for both lexer and parser)

python run.py clean – clean temporary files

Command Line Interface(direct)

# Basic usage
python -m src.cli lex --input <source_file> [--output <tokens_file>]
python -m src.cli parse --input <source_file> [--output <ast_file>] [--format text|dot]

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
python run.py test

# Run only parser tests
python run.py test-parser

# Run with verbose output
python run.py test --verbose
python run.py test-parser --verbose


Expected output files (.txt) are stored in the repository and are not generated automatically during test runs.
If you modify the lexer or parser, you must manually regenerate them:
python run.py generate

This updates all .txt files in tests/lexer/valid/ and tests/parser/valid/.

#Token Output Format
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
##Sprint 2: Syntax Analysis 
Grammar Specification
The language grammar is defined in src/parser/grammar.txt (EBNF).
Key constructs include:

Program – list of declarations (functions, structs, globals)

Statements – block, if, while, for, return, expression statements, variable declarations

Expressions – with proper precedence and associativity:

Assignment (=, +=, -=, *=, /=)

Logical OR (||)

Logical AND (&&)

Equality (==, !=)

Relational (<, <=, >, >=)

Additive (+, -)

Multiplicative (*, /, %)

Unary (-, !)

Primary (literals, identifiers, parenthesized, calls)

Parser Implementation
Recursive descent parser with 1-token lookahead.

Error handling – syntax errors reported with line/column; basic recovery.

AST nodes – well-defined hierarchy (ExpressionNode, StatementNode, DeclarationNode).

Abstract Syntax Tree (AST)
The parser produces an AST that can be output in:

Text format – human-readable with indentation.

DOT format – for visualization with Graphviz.

#Usage Examples
Parse a source file
# Text output (default)
python run.py parse --input examples/factorial.src

# Save to file
python run.py parse --input examples/factorial.src --output ast.txt

# Generate DOT file
python run.py parse --input examples/factorial.src --format dot --output ast.dot

# Convert DOT to PNG (requires graphviz)
dot -Tpng ast.dot -o ast.png

Example Input (examples/example.src)

fn main() -> void {
    int a = 5;
    int b = 10;
    if (a < b) {
        return a;
    } else {
        return b;
    }
}


AST Output (text format)
Program [line 1]:
  FunctionDecl: main -> void [line 1]:
    Parameters:
    Body:
      Block [line 1]:
        VarDecl: int a = 5 [line 2]
        VarDecl: int b = 10 [line 3]
        IfStmt [line 4]:
          Condition: (a < b)
          Then:
            Block [line 4]:
              Return: a [line 5]
          Else:
            Block [line 6]:
              Return: b [line 7]

#Extending the Parser
Add new AST node classes in src/parser/ast.py.

Extend the grammar and implement parsing methods in src/parser/parser.py.

Update the printer(s) in ast_printer.py.

Add tests in tests/parser/ and regenerate expected outputs (python run.py generate).



## Sprint 3: Semantic Analysis (Complete)

### Overview

The semantic analyzer validates the meaning of the program:
- Checks declarations and scopes
- Performs type checking for expressions, assignments, and function calls
- Reports detailed errors with location information
- Decorates the AST with type information for later code generation

### Symbol Table

The symbol table manages identifiers across nested scopes:

- **Global scope** – functions, structs, global variables
- **Function scope** – parameters and local variables
- **Block scope** – inside `{ ... }` (if, while, for)
- **Struct scope** – field names

Each symbol stores:
- Name, kind (variable, function, parameter, struct, field)
- Type (primitive, struct, function, array)
- Declaration location (line, column)
- Additional info for functions (parameters) and structs (fields)

### Type System

Built‑in primitive types: `int`, `float`, `bool`, `void`, `string`

Type compatibility rules:
- `int` can be implicitly converted to `float` (widening)
- No implicit conversion from `float` to `int`
- Assignment requires compatible types (LHS must be assignable)
- Binary operators follow numeric promotion rules
- Logical operators require `bool` operands

### Usage

Run semantic analysis on a source file:

```bash
# Basic check (outputs decorated AST or errors)
python run.py semantic --input examples/program.src

# Save output to file
python run.py semantic --input examples/program.src --output analysis.txt

# Dump symbol table
python run.py semantic --input examples/program.src --symbols

# Run semantic tests
python run.py test-semantic
Direct CLI:

bash
python -m src.cli semantic --input program.src [--output out.txt] [--symbols]
Error Reporting Example
text
type_mismatch: Cannot assign float to int at 5:9
   |
   |     int x = 3.14;
   |             ^^^^
   |
   = expected: int
   = found: float
Testing
Semantic tests are located in tests/semantic/:

Valid tests – programs that must pass without errors.

Invalid tests – programs that contain semantic errors; each has an .expected file with the exact error messages.

Run all semantic tests:

bash
python test_semantic.py
Generate expected outputs for invalid tests (after modifying the analyzer):

bash
python test_semantic.py --generate
Next Steps
Sprint 4 will introduce an intermediate representation (IR) and simple code generation.

text

---

## 4. Запуск и проверка

После создания всех файлов:

1. Сгенерируйте эталонные файлы для invalid тестов:
   ```bash
   python test_semantic.py --generate
Запустите все семантические тесты:

bash
python test_semantic.py

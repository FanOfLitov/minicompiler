# MiniCompiler

MiniCompiler — учебный компилятор для упрощённого C-like языка. Проект реализуется по спринтам: лексический анализ, синтаксический анализ, построение AST, семантический анализ, таблица символов и базовая система типов.

Проект написан на Python и предназначен для демонстрации основных этапов работы компилятора.

## Реализованные этапы

### Sprint 1 — Lexer / Scanner

Реализован лексический анализатор, который читает исходный код и преобразует его в поток токенов.

Поддерживаются:

- ключевые слова: `fn`, `struct`, `if`, `else`, `while`, `for`, `return`, `int`, `float`, `bool`, `void`, `true`, `false`;
- идентификаторы;
- целочисленные, вещественные, строковые и булевы литералы;
- арифметические операторы: `+`, `-`, `*`, `/`, `%`;
- операторы сравнения: `==`, `!=`, `<`, `<=`, `>`, `>=`;
- логические операторы: `&&`, `||`, `!`;
- операторы присваивания: `=`, `+=`, `-=`, `*=`, `/=`;
- разделители: `(`, `)`, `{`, `}`, `[`, `]`, `;`, `,`, `:`, `->`;
- однострочные и многострочные комментарии;
- сообщения об ошибках лексического анализа.

### Sprint 2 — Parser / AST

Реализован рекурсивный синтаксический анализатор, который строит AST.

Поддерживаются:

- объявления функций;
- объявления структур;
- объявления переменных;
- блоки кода;
- условные операторы `if / else`;
- циклы `while` и `for`;
- операторы `return`;
- выражения с приоритетами операторов;
- вызовы функций;
- присваивания;
- текстовый, DOT и JSON-подобный вывод AST.

### Sprint 3 — Semantic Analysis

Реализован семантический анализатор.

Поддерживаются:

- таблица символов;
- вложенные области видимости;
- регистрация функций и структур;
- проверка повторных объявлений;
- проверка неизвестных идентификаторов;
- проверка типов в выражениях;
- проверка типов в присваиваниях;
- проверка аргументов при вызове функций;
- проверка типов возвращаемых значений;
- проверка условий в `if`, `while`, `for`;
- сообщения об ошибках семантического анализа.

## Структура проекта

```text
minicompiler/
├── docs/
├── examples/
│   └── hello.src
├── src/
│   ├── cli.py
│   ├── lexer/
│   │   ├── scanner.py
│   │   ├── token_types.py
│   │   └── __init__.py
│   ├── parser/
│   │   ├── ast_nodes.py
│   │   ├── ast_printer.py
│   │   ├── parser.py
│   │   └── __init__.py
│   ├── semantic/
│   │   ├── analyzer.py
│   │   ├── errors.py
│   │   ├── symbol_table.py
│   │   ├── type_system.py
│   │   └── __init__.py
│   └── utils/
│       ├── error_reporter.py
│       └── __init__.py
├── tests/
│   ├── lexer/
│   │   ├── valid/
│   │   ├── invalid/
│   │   └── test_scanner.py
│   ├── parser/
│   │   ├── valid/
│   │   ├── invalid/
│   │   └── test_parser.py
│   └── semantic/
│       ├── valid/
│       ├── invalid/
│       └── test_semantic.py
├── main.py
├── run.py
├── setup.py
└── README.md
```

## Требования

Рекомендуемая версия Python:

```bash
Python 3.10+
```

Установка зависимостей для тестирования:

```bash
py -m pip install pytest
```

## Запуск тестов

Запустить все тесты:

```bash
py run.py test
```

или напрямую через pytest:

```bash
py -m pytest tests/ -v
```

Запустить только lexer-тесты:

```bash
py -m pytest tests/lexer -v
```

Запустить только parser-тесты:

```bash
py -m pytest tests/parser -v
```

Запустить только semantic-тесты:

```bash
py -m pytest tests/semantic -v
```

## Использование CLI

### Лексический анализ

```bash
py main.py lex --input examples/hello.src
```

С сохранением результата в файл:

```bash
py main.py lex --input examples/hello.src --output tokens.txt
```

### Синтаксический анализ

Вывести AST в текстовом формате:

```bash
py main.py parse --input examples/hello.src --format text
```

Вывести AST в DOT-формате:

```bash
py main.py parse --input examples/hello.src --format dot --output ast.dot
```

### Семантический анализ

```bash
py main.py semantic --input examples/hello.src
```

С выводом таблицы символов:

```bash
py main.py semantic --input examples/hello.src --symbols
```

## Пример исходного кода

```c
fn add(a: int, b: int) -> int {
    return a + b;
}

fn main() -> int {
    int result = add(2, 3);
    return result;
}
```

## Формат lexer-тестов

Для валидных lexer-тестов используется пара файлов:

```text
tests/lexer/valid/example.src
tests/lexer/valid/example.txt
```

Файл `.src` содержит исходный код, а `.txt` содержит ожидаемый поток токенов.

Пример:

```text
1:1 KW_FN "fn"
1:4 IDENTIFIER "main"
1:8 LPAREN "("
1:9 RPAREN ")"
1:11 ARROW "->"
1:14 KW_INT "int"
```

Для невалидных lexer-тестов используются файлы в:

```text
tests/lexer/invalid/
```

Такие тесты должны приводить к ошибке лексического анализа.

## Формат parser-тестов

Валидные parser-тесты находятся в:

```text
tests/parser/valid/
```

Для каждого `.src` есть соответствующий `.expected`, с которым сравнивается текстовое представление AST.

Невалидные parser-тесты находятся в:

```text
tests/parser/invalid/
```

Они проверяют, что парсер корректно сообщает о синтаксических ошибках.

## Формат semantic-тестов

Валидные semantic-тесты находятся в:

```text
tests/semantic/valid/
```

Для них `.expected` не требуется. Тест считается успешным, если семантический анализ завершился без ошибок.

Невалидные semantic-тесты находятся в:

```text
tests/semantic/invalid/
```

Для них используется пара:

```text
example.src
example.expected
```

Файл `.expected` содержит ожидаемое сообщение об ошибке.

## Пример семантической ошибки

```c
fn main() -> void {
    int x;
    x = 3.14;
}
```

Ожидаемая ошибка:

```text
semantic error at type_mismatch_assignment.src:3:5: type mismatch in assignment to 'x': expected int, got float
```

## Полезные команды

Очистить временные файлы:

```bash
py run.py clean
```

Вывести структуру проекта:

```bash
tree /f
```

На Linux/macOS:

```bash
tree
```

## Текущее состояние

На данный момент реализованы основные части первых трёх спринтов:

- scanner;
- token definitions;
- parser;
- AST nodes;
- AST printer;
- semantic analyzer;
- symbol table;
- type system;
- semantic error reporter;
- pytest-наборы для lexer, parser и semantic.

дальше Sprint 4: промежуточное представление IR и генерация IR 

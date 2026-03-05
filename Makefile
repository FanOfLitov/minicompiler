.PHONY: all build test clean run

all: build test

build:
	@echo "Building MiniCompiler..."

test:
	python test_runner.py

test-verbose:
	python test_runner.py --verbose

test-generate:
	python test_runner.py --generate

run:
	python -m src.cli lex --input examples/hello.src

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
	rm -f tokens.txt

help:
	@echo "Available commands:"
	@echo "  make build    - Build the project"
	@echo "  make test     - Run all tests"
	@echo "  make run      - Run lexer on example"
	@echo "  make clean    - Clean generated files"
	@echo "  make help     - Show this help"
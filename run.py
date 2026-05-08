#!/usr/bin/env python3
"""
MiniCompiler - Automation script with deep diagnostics.
Compatible with Python 3.8+ on Windows/Linux/macOS.
"""
import sys
import os
import shutil
import subprocess
from pathlib import Path

# Принудительный вывод без буферизации для моментальной диагностики в Windows
print("[DEBUG] run.py started successfully.", flush=True)

PYTHON_EXE = sys.executable
BASE_DIR = Path(__file__).resolve().parent
EXAMPLES_DIR = BASE_DIR / "examples"
EXAMPLE_FILE = EXAMPLES_DIR / "factorial.src"

print(f"[DEBUG] Python Executable: {PYTHON_EXE}", flush=True)
print(f"[DEBUG] Base Directory: {BASE_DIR}", flush=True)


def log(msg: str):
    print(f"\n>>> [MINICC RUNNER] {msg}", flush=True)


def run_command(cmd_args, check=True):
    print(f"Executing: {' '.join(str(x) for x in cmd_args)}", flush=True)
    try:
        result = subprocess.run(cmd_args, check=check, capture_output=False, text=True)
        return result.returncode
    except Exception as e:
        print(f"[ERROR] Failed to execute command: {e}", flush=True)
        return 1


def clean():
    log("Cleaning up compiled and temporary files...")
    count = 0
    for p in list(BASE_DIR.rglob("__pycache__")):
        if p.is_dir():
            print(f"Removing directory: {p}", flush=True)
            shutil.rmtree(p)
            count += 1
    for p in list(BASE_DIR.rglob("*.pyc")):
        print(f"Removing file: {p}", flush=True)
        p.unlink()
        count += 1
    for file_name in ["ast.dot", "ast.png", "tokens.txt"]:
        file_path = BASE_DIR / file_name
        if file_path.exists():
            print(f"Removing: {file_path}", flush=True)
            file_path.unlink()
            count += 1
    log(f"Clean completed. Cleared {count} items.")


def run_tests(module=None):
    log("Verifying pytest installation...")
    try:
        import pytest
        print(f"[DEBUG] pytest is available (version {pytest.__version__})", flush=True)
    except ImportError:
        print("[ERROR] 'pytest' is not installed in this environment!", flush=True)
        print(f"Please run: {PYTHON_EXE} -m pip install pytest", flush=True)
        sys.exit(1)

    # Добавляем корень проекта в PYTHONPATH для корректного импорта модулей в тестах
    os.environ["PYTHONPATH"] = str(BASE_DIR)

    cmd = [PYTHON_EXE, "-m", "pytest"]
    if module:
        cmd.append(f"tests/{module}/")
    else:
        cmd.append("tests/")
    cmd.append("-v")

    code = run_command(cmd, check=False)
    sys.exit(code)


def run_lex():
    log("Running Lexer...")
    run_command([PYTHON_EXE, "main.py", "lex", "-i", str(EXAMPLE_FILE)])


def run_parse(fmt="text"):
    log(f"Running Parser (Format: {fmt})...")
    cmd = [PYTHON_EXE, "main.py", "parse", "-i", str(EXAMPLE_FILE), "-f", fmt]
    if fmt == "dot":
        cmd.extend(["-o", "ast.dot"])
    run_command(cmd)


def check_semantics():
    log("Running Semantic Analysis...")
    run_command([PYTHON_EXE, "main.py", "check", "-i", str(EXAMPLE_FILE), "-v"])


def compile_pipeline():
    log("Running complete pipeline...")
    run_command([PYTHON_EXE, "main.py", "compile", "-i", str(EXAMPLE_FILE)])


def print_help():
    print("""
MiniCompiler Automation Task Manager (run.py)
---------------------------------------------
Usage:
    python run.py <task>

Available Tasks:
    test            - Runs all tests
    test-lexer      - Runs lexer tests
    test-parser     - Runs parser tests
    test-semantic   - Runs semantic tests
    lex             - Tokenize examples/factorial.src
    parse           - Parse examples/factorial.src to text AST
    parse-dot       - Generate Graphviz 'ast.dot'
    check           - Perform semantic analysis & show tables
    compile         - Run full compiler pipeline
    clean           - Cleanup all temp files and caches
""", flush=True)


def main():
    if len(sys.argv) < 2:
        print_help()
        sys.exit(0)

    task = sys.argv[1].lower()
    print(f"[DEBUG] Target task selected: {task}", flush=True)

    if task == "clean":
        clean()
    elif task == "test":
        run_tests()
    elif task == "test-lexer":
        run_tests("lexer")
    elif task == "test-parser":
        run_tests("parser")
    elif task == "test-semantic":
        run_tests("semantic")
    elif task == "lex":
        run_lex()
    elif task == "parse":
        run_parse("text")
    elif task == "parse-dot":
        run_parse("dot")
    elif task == "check":
        check_semantics()
    elif task == "compile":
        compile_pipeline()
    else:
        print(f"Unknown task: '{task}'", flush=True)
        print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
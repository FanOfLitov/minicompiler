#!/usr/bin/env bash

# MiniCompiler defense demo script.
# Run from project root:
#   bash scripts/defense_demo.sh
#
# The script automatically chooses a usable Python command.
# On Windows Git Bash, /usr/bin/py is often NOT Python Launcher,
# so we prefer python3/python/python.exe and only then py.

set +e

detect_python() {

    # Windows Python Launcher
    if command -v py.exe >/dev/null 2>&1; then
        echo "py.exe"
        return 0
    fi

    # Windows python
    if command -v python.exe >/dev/null 2>&1; then
        echo "python.exe"
        return 0
    fi

    # fallback
    if command -v py >/dev/null 2>&1; then
        echo "py"
        return 0
    fi

    if command -v python >/dev/null 2>&1; then
        echo "python"
        return 0
    fi

    return 1
}

PY=${PYTHON_CMD:-$(detect_python)}

if [ -z "$PY" ]; then
    echo "ERROR: Python was not found."
    echo "Try running one of these manually:"
    echo "  python --version"
    echo "  python3 --version"
    echo "  python.exe --version"
    echo "  py --version"
    exit 1
fi

run_cmd() {
    echo
    echo "$ $*"
    "$@"
    code=$?
    if [ $code -ne 0 ]; then
        echo "[warning] command failed with code $code, continuing demo..."
    fi
    echo
}

echo "============================================================"
echo "MiniCompiler Defense Demo"
echo "============================================================"
echo

echo "[0] Environment"
echo "Selected Python command: $PY"
run_cmd "$PY" --version

echo "Project tree:"
if command -v tree >/dev/null 2>&1; then
    tree -L 3
else
    find . -maxdepth 3 -type f | sort
fi
echo

echo "============================================================"
echo "[Sprint 1] Lexer / Scanner"
echo "============================================================"
run_cmd "$PY" main.py lex --input examples/demo/merge_sort.src
run_cmd "$PY" -m pytest tests/lexer -v

echo "============================================================"
echo "[Sprint 2] Parser / AST"
echo "============================================================"
run_cmd "$PY" main.py parse --input examples/demo/merge_sort.src --format text
run_cmd "$PY" -m pytest tests/parser -v

echo "============================================================"
echo "[Sprint 3] Semantic Analysis"
echo "============================================================"
run_cmd "$PY" main.py semantic --input examples/demo/merge_sort.src --symbols
run_cmd "$PY" -m pytest tests/semantic -v

echo "============================================================"
echo "[Sprint 4] IR Generation"
echo "============================================================"

echo
echo "Source:"
echo "examples/demo/ir_demo.src"
echo

cat examples/demo/ir_demo.src
echo

echo "------------------------------------------------------------"
echo "Generated IR"
echo "------------------------------------------------------------"
echo

$PY main.py ir --input examples/demo/ir_demo.src || true

echo
echo "------------------------------------------------------------"
echo "IR tests"
echo "------------------------------------------------------------"
echo

$PY -m pytest tests/ir -v || true

echo

echo "============================================================"
echo "[Sprint 5] x86-64 Code Generation"
echo "============================================================"
mkdir -p build
run_cmd "$PY" main.py asm --input examples/demo/merge_sort.src --output build/merge_sort.asm

if [ -f build/merge_sort.asm ]; then
    echo "Generated assembly preview:"
    sed -n '1,120p' build/merge_sort.asm
fi

run_cmd "$PY" -m pytest tests/codegen -v

echo "============================================================"
echo "[Sprint 6] IR Optimizer"
echo "============================================================"
run_cmd "$PY" main.py asm --input examples/demo/sprint7_optimization_demo.src --output build/optimized.asm --optimize

if [ -f build/optimized.asm ]; then
    echo "Optimized assembly preview:"
    sed -n '1,120p' build/optimized.asm
fi

run_cmd "$PY" -m pytest tests/optimizer -v

echo "============================================================"
echo "[Sprint 7] Advanced Features"
echo "============================================================"
run_cmd "$PY" -m pytest tests/sprint7 -v

echo "============================================================"
echo "Defense demo completed."
echo "============================================================"

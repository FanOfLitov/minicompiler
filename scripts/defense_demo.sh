#!/usr/bin/env bash
set +e

detect_python() {
    for candidate in python.exe python py.exe py python3; do
        if command -v "$candidate" >/dev/null 2>&1; then
            if "$candidate" -c "import sys; print(sys.version)" >/dev/null 2>&1; then
                echo "$candidate"
                return 0
            fi
        fi
    done
    return 1
}

PY=${PYTHON_CMD:-$(detect_python)}

if [ -z "$PY" ]; then
    echo "ERROR: Python was not found."
    exit 1
fi

mkdir -p build

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
echo "[Sprint 4] Intermediate Representation: IR and SSA"
echo "============================================================"

echo
echo "This sprint demonstrates the required middle layer:"
echo "source -> lexer -> parser -> AST -> semantic -> IR -> SSA IR -> ASM"
echo
echo "Source file:"
echo "examples/demo/ir_ssa_demo.src"
echo "------------------------------------------------------------"
cat examples/demo/ir_ssa_demo.src
echo

echo "------------------------------------------------------------"
echo "Step 4.1: Normal IR / three-address code"
echo "This is NOT assembly. It is compiler intermediate representation."
echo "------------------------------------------------------------"
run_cmd "$PY" main.py ir --input examples/demo/ir_ssa_demo.src

echo "------------------------------------------------------------"
echo "Step 4.2: SSA-like IR"
echo "Each assignment gets a visible version: x.1, x.2, t1_1..."
echo "------------------------------------------------------------"
run_cmd "$PY" main.py ssa --input examples/demo/ir_ssa_demo.src

echo "------------------------------------------------------------"
echo "Step 4.3: IR tests"
echo "------------------------------------------------------------"
run_cmd "$PY" -m pytest tests/ir -v

echo "------------------------------------------------------------"
echo "Step 4.4: SSA tests"
echo "------------------------------------------------------------"
run_cmd "$PY" -m pytest tests/ssa -v

echo "============================================================"
echo "[Sprint 5] x86-64 Code Generation"
echo "============================================================"
echo "Assembly is generated ONLY after the IR and SSA steps above."
run_cmd "$PY" main.py asm --input examples/demo/ir_ssa_demo.src --output build/ir_ssa_demo.asm

if [ -f build/ir_ssa_demo.asm ]; then
    echo "Generated assembly preview:"
    sed -n '1,120p' build/ir_ssa_demo.asm
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
echo "[Sprint 8] Full Pipeline Integration"
echo "============================================================"
if [ -d tests/sprint8 ]; then
    run_cmd "$PY" -m pytest tests/sprint8 -v
fi

if [ -f scripts/full_build_demo.sh ]; then
    echo "Full build demo script exists: scripts/full_build_demo.sh"
fi

echo "============================================================"
echo "Defense demo completed."
echo "============================================================"

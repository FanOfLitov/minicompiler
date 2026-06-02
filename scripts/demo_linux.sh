#!/usr/bin/env bash
set -u

PY="${PYTHON_CMD:-python3}"

run() {
    echo
    echo "$ $*"
    "$@"
    code=$?
    if [ $code -ne 0 ]; then
        echo "[warning] command failed with code $code, continuing demo..."
    fi
    echo
}

pause_step() {
    if [ "${DEMO_PAUSE:-0}" = "1" ]; then
        read -r -p "Press Enter to continue..."
    fi
}

echo "============================================================"
echo "MiniCompiler Linux Defense Demo"
echo "============================================================"
echo

echo "[0] Environment"
echo "Selected Python: $PY"
run "$PY" --version

echo "Project tree preview:"
if command -v tree >/dev/null 2>&1; then
    tree -L 3
else
    find . -maxdepth 3 -type f | sort | head -120
fi

mkdir -p build
pause_step

echo "============================================================"
echo "[Sprint 1] Lexer / Scanner"
echo "============================================================"
run "$PY" main.py lex --input examples/demo/ir_ssa_demo.src
run "$PY" -m pytest tests/lexer -v
pause_step

echo "============================================================"
echo "[Sprint 2] Parser / AST"
echo "============================================================"
run "$PY" main.py parse --input examples/demo/ir_ssa_demo.src --format text
run "$PY" -m pytest tests/parser -v
pause_step

echo "============================================================"
echo "[Sprint 3] Semantic Analysis"
echo "============================================================"
run "$PY" main.py semantic --input examples/demo/ir_ssa_demo.src --symbols
run "$PY" -m pytest tests/semantic -v
pause_step

echo "============================================================"
echo "[Sprint 4] IR and SSA Intermediate Representation"
echo "============================================================"
echo "source -> lexer -> parser -> AST -> semantic -> IR -> SSA -> ASM"
echo
echo "Source program:"
cat examples/demo/ir_ssa_demo.src
echo
echo "Normal IR:"
run "$PY" main.py ir --input examples/demo/ir_ssa_demo.src
echo "SSA IR:"
run "$PY" main.py ssa --input examples/demo/ir_ssa_demo.src
run "$PY" -m pytest tests/ir -v
run "$PY" -m pytest tests/ssa -v
pause_step

echo "============================================================"
echo "[Sprint 5] x86-64 Code Generation"
echo "============================================================"
run "$PY" main.py asm --input examples/demo/ir_ssa_demo.src --output build/ir_ssa_demo.asm
if [ -f build/ir_ssa_demo.asm ]; then
    echo "ASM preview:"
    sed -n '1,100p' build/ir_ssa_demo.asm
fi
run "$PY" -m pytest tests/codegen -v
pause_step

echo "============================================================"
echo "[Sprint 6] Optimizer"
echo "============================================================"
run "$PY" main.py ir --input examples/demo/sprint7_optimization_demo.src
run "$PY" main.py asm --input examples/demo/sprint7_optimization_demo.src --output build/optimized.asm
run "$PY" -m pytest tests/optimizer -v
pause_step

echo "============================================================"
echo "[Sprint 7] Dynamic arrays, heap, ALLOCA -> MALLOC, merge sort"
echo "============================================================"
echo "Dynamic array runtime demo:"
PYTHONPATH=. "$PY" examples/demo/sprint7_dynamic_array_demo.py || true

echo
echo "ALLOCA -> MALLOC demo:"
PYTHONPATH=. "$PY" examples/demo/sprint7_malloc_array_demo.py || true

echo
echo "Real merge sort array pipeline:"
PYTHONPATH=. "$PY" examples/demo/rebuild_merge_sort_real_pipeline.py || true

echo
echo "Key ASM lines:"
grep -nE "extern malloc|call malloc|merge_sort:|merge:|call merge_sort|call merge|copy_temp_back" build/merge_sort.asm || true

run "$PY" -m pytest tests/sprint7/test_dynamic_array_allocator.py -v
run "$PY" -m pytest tests/sprint7/test_heap_array_lowering.py -v
run "$PY" -m pytest tests/sprint7/test_real_merge_sort_pipeline.py -v
pause_step

echo "============================================================"
echo "[Sprint 8] Full Pipeline Integration"
echo "============================================================"
run "$PY" -m pytest tests/sprint8 -v

echo "Generated build artifacts:"
ls -la build || true

echo "============================================================"
echo "Demo completed."
echo "============================================================"

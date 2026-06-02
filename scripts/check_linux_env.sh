#!/usr/bin/env bash
set -u
PY="${PYTHON_CMD:-python3}"

echo "============================================================"
echo "MiniCompiler Linux Environment Check"
echo "============================================================"

echo "[Python]"
if command -v "$PY" >/dev/null 2>&1; then
    "$PY" --version
else
    echo "Python not found. Install: sudo apt install python3 python3-pip"
fi

echo
echo "[pytest]"
"$PY" -m pytest --version 2>/dev/null || {
    echo "pytest not found."
    echo "Install:"
    echo "  $PY -m pip install pytest pytest-timeout pytest-xdist pytest-benchmark"
}

echo
echo "[optional tools]"
for tool in tree nasm gcc; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo "$tool: OK"
    else
        echo "$tool: missing"
    fi
done

echo
echo "[project files]"
for path in main.py src/lexer src/parser src/semantic src/ir src/ssa src/codegen src/arrays src/runtime examples/demo/ir_ssa_demo.src examples/demo/rebuild_merge_sort_real_pipeline.py tests/sprint7 tests/sprint8; do
    if [ -e "$path" ]; then
        echo "$path: OK"
    else
        echo "$path: MISSING"
    fi
done

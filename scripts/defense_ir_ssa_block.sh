#!/usr/bin/env bash
PY=${PYTHON_CMD:-python.exe}

echo "============================================================"
echo "[Sprint 4] IR and SSA Intermediate Representation"
echo "============================================================"

echo "Source:"
cat examples/demo/ir_ssa_demo.src

echo
echo "Normal IR:"
"$PY" main.py ir --input examples/demo/ir_ssa_demo.src

echo
echo "SSA IR:"
"$PY" main.py ssa --input examples/demo/ir_ssa_demo.src

echo
echo "ASM only after IR/SSA:"
"$PY" main.py asm --input examples/demo/ir_ssa_demo.src --output build/ir_ssa_demo.asm

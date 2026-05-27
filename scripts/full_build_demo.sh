#!/usr/bin/env bash
set +e

PY=${PYTHON_CMD:-py.exe}

mkdir -p build

echo "Sprint 8 full pipeline demo"
echo "Selected Python: $PY"
echo "Input: examples/demo/sprint8_full_pipeline.src"

"$PY" main.py lex --input examples/demo/sprint8_full_pipeline.src
"$PY" main.py parse --input examples/demo/sprint8_full_pipeline.src --format text
"$PY" main.py semantic --input examples/demo/sprint8_full_pipeline.src --symbols
"$PY" main.py ir --input examples/demo/sprint8_full_pipeline.src
"$PY" main.py ssa --input examples/demo/sprint8_full_pipeline.src
"$PY" main.py asm --input examples/demo/sprint8_full_pipeline.src --output build/sprint8_full_pipeline.asm

echo "Assembly saved to build/sprint8_full_pipeline.asm"

#!/usr/bin/env bash
set +e

detect_python() {
    for candidate in python.exe python3 python py.exe py; do
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
    echo "Python not found"
    exit 1
fi

mkdir -p build

echo "Sprint 8 full pipeline demo"
echo "Selected Python: $PY"
echo "Input: examples/demo/sprint8_full_pipeline.src"

"$PY" main.py lex --input examples/demo/sprint8_full_pipeline.src
"$PY" main.py parse --input examples/demo/sprint8_full_pipeline.src --format text
"$PY" main.py semantic --input examples/demo/sprint8_full_pipeline.src --symbols
"$PY" main.py ir --input examples/demo/sprint8_full_pipeline.src
"$PY" main.py asm --input examples/demo/sprint8_full_pipeline.src --output build/sprint8_full_pipeline.asm --optimize

echo "Assembly saved to build/sprint8_full_pipeline.asm"

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.codegen.malloc_asm_generator import MallocArrayASMGenerator


def main():
    output_path = ROOT / "build" / "sprint7_malloc_array.asm"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    values = [8, 3, 5, 1, 9]
    asm = MallocArrayASMGenerator().generate_int_array_demo("arr", values, element_size=8)

    output_path.write_text(asm + "\n", encoding="utf-8")

    print("Sprint 7 malloc array ASM demo")
    print("=" * 70)
    print("Generated:", output_path)
    print()
    print(asm)


if __name__ == "__main__":
    main()

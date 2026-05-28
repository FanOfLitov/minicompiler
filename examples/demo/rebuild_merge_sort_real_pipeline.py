import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.arrays.merge_sort_ir_builder import MergeSortIRBuilder
from src.arrays.array_heap_lowering import ArrayHeapLowering
from src.codegen.array_ir_x86_generator import ArrayIRX86Generator


def main():
    values = [8, 3, 5, 1, 9, 2, 7, 4]

    high_ir = MergeSortIRBuilder().build(values)
    lowered_ir = ArrayHeapLowering().lower(high_ir)
    asm = ArrayIRX86Generator().generate(lowered_ir)

    build_dir = ROOT / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    (build_dir / "merge_sort.high.ir").write_text(high_ir.dump() + "\n", encoding="utf-8")
    (build_dir / "merge_sort.lowered.ir").write_text(lowered_ir.dump() + "\n", encoding="utf-8")
    (build_dir / "merge_sort.asm").write_text(asm + "\n", encoding="utf-8")

    print("Real Merge Sort array pipeline")
    print("=" * 80)
    print()
    print("High-level IR:")
    print("-" * 80)
    print(high_ir.dump())
    print()
    print("Lowered IR:")
    print("-" * 80)
    print(lowered_ir.dump())
    print()
    print("Generated ASM:")
    print("-" * 80)
    print(asm)
    print()
    print("Files written:")
    print(build_dir / "merge_sort.high.ir")
    print(build_dir / "merge_sort.lowered.ir")
    print(build_dir / "merge_sort.asm")


if __name__ == "__main__":
    main()

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.runtime.heap_allocator import HeapAllocator
from src.runtime.dynamic_array import DynamicArray


def main():
    print("Sprint 7 Dynamic Array + Heap Allocator Demo")
    print("=" * 60)

    allocator = HeapAllocator()
    array = DynamicArray(allocator=allocator, length=5, element_size=8)

    print("malloc length * element_size")
    print("array pointer =", array.ptr)
    print()

    values = [8, 3, 5, 1, 9]

    for index, value in enumerate(values):
        array.set(index, value)
        print("arr[{}] -> heap[{}] = {}".format(index, array.address_of(index), value))

    print()
    print("Array output:")
    print(array.print_array())

    print()
    print(array.dump_layout())

    print()
    print(allocator.dump())


if __name__ == "__main__":
    main()

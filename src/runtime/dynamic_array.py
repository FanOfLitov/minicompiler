from dataclasses import dataclass
from typing import List

from src.runtime.heap_allocator import HeapAllocator


class DynamicArrayError(RuntimeError):
    pass


@dataclass
class DynamicArray:
    allocator: HeapAllocator
    length: int
    element_size: int = 8

    def __post_init__(self) -> None:
        if self.length <= 0:
            raise DynamicArrayError("array length must be positive")
        if self.element_size <= 0:
            raise DynamicArrayError("element size must be positive")

        self.ptr = self.allocator.malloc(self.length * self.element_size)

    def address_of(self, index: int) -> int:
        self._check_index(index)
        return self.ptr + index * self.element_size

    def set(self, index: int, value: int) -> None:
        self._check_index(index)
        self.allocator.write(
            self.ptr,
            index * self.element_size,
            value,
            self.element_size,
        )

    def get(self, index: int) -> int:
        self._check_index(index)
        return self.allocator.read(
            self.ptr,
            index * self.element_size,
            self.element_size,
        )

    def values(self) -> List[int]:
        return [self.get(i) for i in range(self.length)]

    def free(self) -> None:
        self.allocator.free(self.ptr)

    def dump_layout(self) -> str:
        lines = [
            "DYNAMIC ARRAY",
            "  ptr: {}".format(self.ptr),
            "  length: {}".format(self.length),
            "  element_size: {}".format(self.element_size),
            "  total_bytes: {}".format(self.length * self.element_size),
        ]

        for index in range(self.length):
            lines.append(
                "  arr[{}] -> heap[{}] = {}".format(
                    index,
                    self.address_of(index),
                    self.get(index),
                )
            )

        return "\n".join(lines)

    def print_array(self) -> str:
        return "[" + ", ".join(str(value) for value in self.values()) + "]"

    def _check_index(self, index: int) -> None:
        if index < 0 or index >= self.length:
            raise DynamicArrayError(
                "array index out of bounds: index={}, length={}".format(
                    index,
                    self.length,
                )
            )

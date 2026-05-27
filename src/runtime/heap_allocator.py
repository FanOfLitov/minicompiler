from dataclasses import dataclass, field
from typing import Dict, List


class HeapAllocatorError(RuntimeError):
    pass


@dataclass
class HeapBlock:
    ptr: int
    size: int
    freed: bool = False

    @property
    def end(self) -> int:
        return self.ptr + self.size


@dataclass
class HeapAllocator:
    start_address: int = 1000
    next_address: int = 1000
    memory: Dict[int, int] = field(default_factory=dict)
    blocks: Dict[int, HeapBlock] = field(default_factory=dict)

    def malloc(self, size: int) -> int:
        if size <= 0:
            raise HeapAllocatorError("malloc size must be positive")

        ptr = self.next_address
        self.blocks[ptr] = HeapBlock(ptr=ptr, size=size)

        for address in range(ptr, ptr + size):
            self.memory[address] = 0

        self.next_address += size
        return ptr

    def free(self, ptr: int) -> None:
        block = self._get_block(ptr)

        if block.freed:
            raise HeapAllocatorError("double free detected at address {}".format(ptr))

        block.freed = True

    def write(self, ptr: int, offset: int, value: int, size: int = 8) -> None:
        block = self._get_live_block(ptr)
        self._check_range(block, offset, size)
        self.memory[ptr + offset] = value

    def read(self, ptr: int, offset: int, size: int = 8) -> int:
        block = self._get_live_block(ptr)
        self._check_range(block, offset, size)
        return self.memory[ptr + offset]

    def dump(self) -> str:
        lines: List[str] = ["HEAP DUMP"]

        if not self.blocks:
            lines.append("  <empty>")
            return "\n".join(lines)

        for ptr in sorted(self.blocks):
            block = self.blocks[ptr]
            state = "freed" if block.freed else "active"
            lines.append("  block ptr={} size={} state={}".format(block.ptr, block.size, state))

            if not block.freed:
                for address in sorted(self.memory):
                    if block.ptr <= address < block.end and self.memory[address] != 0:
                        lines.append("    [{}] = {}".format(address, self.memory[address]))

        return "\n".join(lines)

    def _get_block(self, ptr: int) -> HeapBlock:
        if ptr not in self.blocks:
            raise HeapAllocatorError("invalid pointer {}".format(ptr))
        return self.blocks[ptr]

    def _get_live_block(self, ptr: int) -> HeapBlock:
        block = self._get_block(ptr)
        if block.freed:
            raise HeapAllocatorError("use after free at address {}".format(ptr))
        return block

    def _check_range(self, block: HeapBlock, offset: int, size: int) -> None:
        if offset < 0:
            raise HeapAllocatorError("negative heap offset {}".format(offset))

        if offset + size > block.size:
            raise HeapAllocatorError(
                "heap access out of bounds: offset={}, size={}, block_size={}".format(
                    offset,
                    size,
                    block.size,
                )
            )

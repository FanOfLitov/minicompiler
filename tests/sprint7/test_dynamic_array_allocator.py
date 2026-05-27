import pytest

from src.runtime.heap_allocator import HeapAllocator, HeapAllocatorError
from src.runtime.dynamic_array import DynamicArray, DynamicArrayError


def test_malloc_returns_start_address():
    allocator = HeapAllocator()
    ptr = allocator.malloc(16)

    assert ptr == 1000
    assert allocator.blocks[ptr].size == 16


def test_malloc_places_second_block_after_first():
    allocator = HeapAllocator()
    first = allocator.malloc(16)
    second = allocator.malloc(24)

    assert first == 1000
    assert second == 1016


def test_dynamic_array_addresses_are_sequential():
    allocator = HeapAllocator()
    array = DynamicArray(allocator, length=5, element_size=8)

    assert array.address_of(0) == array.ptr
    assert array.address_of(1) == array.ptr + 8
    assert array.address_of(4) == array.ptr + 32


def test_dynamic_array_write_and_read():
    allocator = HeapAllocator()
    array = DynamicArray(allocator, length=3, element_size=8)

    array.set(0, 10)
    array.set(1, 20)
    array.set(2, 30)

    assert array.get(0) == 10
    assert array.get(1) == 20
    assert array.get(2) == 30
    assert array.values() == [10, 20, 30]


def test_dynamic_array_print_output():
    allocator = HeapAllocator()
    array = DynamicArray(allocator, length=3, element_size=8)

    array.set(0, 8)
    array.set(1, 3)
    array.set(2, 5)

    assert array.print_array() == "[8, 3, 5]"


def test_heap_dump_shows_addresses_and_values():
    allocator = HeapAllocator()
    array = DynamicArray(allocator, length=2, element_size=8)

    array.set(0, 111)
    array.set(1, 222)

    dump = allocator.dump()

    assert "HEAP DUMP" in dump
    assert "[1000] = 111" in dump
    assert "[1008] = 222" in dump


def test_array_layout_dump_shows_heap_mapping():
    allocator = HeapAllocator()
    array = DynamicArray(allocator, length=2, element_size=8)

    array.set(0, 7)
    array.set(1, 9)

    layout = array.dump_layout()

    assert "DYNAMIC ARRAY" in layout
    assert "arr[0] -> heap[1000] = 7" in layout
    assert "arr[1] -> heap[1008] = 9" in layout


def test_invalid_malloc_size_raises_error():
    allocator = HeapAllocator()

    with pytest.raises(HeapAllocatorError):
        allocator.malloc(0)


def test_array_out_of_bounds_raises_error():
    allocator = HeapAllocator()
    array = DynamicArray(allocator, length=2, element_size=8)

    with pytest.raises(DynamicArrayError):
        array.set(2, 100)


def test_use_after_free_raises_error():
    allocator = HeapAllocator()
    array = DynamicArray(allocator, length=2, element_size=8)

    array.free()

    with pytest.raises(HeapAllocatorError):
        array.get(0)

from pathlib import Path


def test_merge_sort_asm_exists():
    path = Path("build/merge_sort.asm")
    assert path.exists()


def test_merge_sort_asm_contains_malloc():
    text = Path("build/merge_sort.asm").read_text(encoding="utf-8")

    assert "extern malloc" in text
    assert "call malloc" in text
    assert "mov rdi, 64" in text


def test_merge_sort_asm_contains_sort_functions():
    text = Path("build/merge_sort.asm").read_text(encoding="utf-8")

    assert "merge_sort:" in text
    assert "merge:" in text


def test_merge_sort_asm_contains_recursive_calls():
    text = Path("build/merge_sort.asm").read_text(encoding="utf-8")

    assert "call merge_sort" in text
    assert "call merge" in text


def test_merge_sort_asm_writes_initial_array_to_heap():
    text = Path("build/merge_sort.asm").read_text(encoding="utf-8")

    assert "mov qword [rbx+0], 8" in text
    assert "mov qword [rbx+8], 3" in text
    assert "mov qword [rbx+56], 4" in text


def test_merge_sort_asm_copies_temp_back_to_original_array():
    text = Path("build/merge_sort.asm").read_text(encoding="utf-8")

    assert ".copy_temp_back:" in text
    assert ".copy_back_loop:" in text
    assert "mov qword [rbx+rax], r10" in text

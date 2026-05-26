from pathlib import Path

import pytest

from src.pipeline import BuildConfig, CompilerPipeline
from src.pipeline.toolchain import Toolchain


BASE_DIR = Path(__file__).parent
VALID_DIR = BASE_DIR / "valid"
INVALID_DIR = BASE_DIR / "invalid"
BUILD_DIR = BASE_DIR / "build"


VALID_PIPELINE_CASES = [
    "01_return_constant.src",
    "02_arithmetic.src",
    "03_if_else.src",
    "04_while.src",
    "05_function_call.src",
    "06_recursive_shape.src",
    "07_optimized.src",
]

INVALID_PIPELINE_CASES = [
    ("01_lexer_error.src", "lex"),
    ("02_parse_error.src", "parse"),
    ("03_semantic_type_error.src", "semantic"),
    ("04_undeclared_variable.src", "semantic"),
    ("05_wrong_return_type.src", "semantic"),
    ("06_wrong_argument_count.src", "semantic"),
    ("07_invalid_condition.src", "semantic"),
]


@pytest.mark.parametrize("case_name", VALID_PIPELINE_CASES)
def test_pipeline_valid_cases_emit_ir_and_asm(case_name):
    src_path = VALID_DIR / case_name
    out_dir = BUILD_DIR / case_name.replace(".src", "")

    config = BuildConfig(
        input_file=src_path,
        output_dir=out_dir,
        output_name="program",
        optimize=case_name == "07_optimized.src",
        emit_ir=True,
        emit_asm=True,
        assemble=False,
        link=False,
    )

    result = CompilerPipeline().compile(config)

    assert result.success is True, result.summary()
    assert result.stage == "codegen"
    assert config.ir_path.exists()
    assert config.asm_path.exists()

    ir_text = config.ir_path.read_text(encoding="utf-8")
    asm_text = config.asm_path.read_text(encoding="utf-8")

    assert "function" in ir_text
    assert "section .text" in asm_text
    assert "global main" in asm_text


@pytest.mark.parametrize("case_name, expected_stage", INVALID_PIPELINE_CASES)
def test_pipeline_invalid_cases_stop_at_expected_stage(case_name, expected_stage):
    src_path = INVALID_DIR / case_name
    out_dir = BUILD_DIR / case_name.replace(".src", "")

    config = BuildConfig(input_file=src_path, output_dir=out_dir)

    result = CompilerPipeline().compile(config)

    assert result.success is False
    assert result.stage == expected_stage
    assert result.diagnostics


def test_build_result_summary_contains_artifacts():
    src_path = VALID_DIR / "01_return_constant.src"
    out_dir = BUILD_DIR / "summary"

    result = CompilerPipeline().compile(BuildConfig(input_file=src_path, output_dir=out_dir))
    summary = result.summary()

    assert "Build status: success" in summary
    assert "Artifacts:" in summary
    assert ".ir" in summary
    assert ".asm" in summary


def test_toolchain_detection_is_safe_without_tools():
    toolchain = Toolchain(nasm="definitely_missing_nasm", gcc="definitely_missing_gcc")
    missing = toolchain.check()

    assert "definitely_missing_nasm" in missing
    assert "definitely_missing_gcc" in missing


def test_assemble_stage_reports_missing_nasm():
    src_path = VALID_DIR / "01_return_constant.src"
    out_dir = BUILD_DIR / "missing_nasm"

    config = BuildConfig(input_file=src_path, output_dir=out_dir, assemble=True)
    pipeline = CompilerPipeline(toolchain=Toolchain(nasm="definitely_missing_nasm", gcc="definitely_missing_gcc"))

    result = pipeline.compile(config)

    assert result.success is False
    assert result.stage == "assemble"
    assert "NASM was not found" in "\n".join(result.diagnostics)

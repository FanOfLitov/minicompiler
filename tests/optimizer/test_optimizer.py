from pathlib import Path

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.ir.ir_generator import IRGenerator
from src.optimizer.optimizer import IROptimizer

VALID_DIR = Path(__file__).parent / "valid"

def _optimized(src_name):
    src = VALID_DIR / src_name
    source = src.read_text(encoding="utf-8")

    scanner = Scanner(source, filename=str(src))
    tokens = scanner.scan_tokens()

    parser = Parser(tokens)
    ast = parser.parse()

    analyzer = SemanticAnalyzer(filename=src.name, source=source)
    assert analyzer.analyze(ast)

    ir = IRGenerator().generate(ast)
    ir = IROptimizer().optimize(ir)

    return ir.dump()

def test_constant_folding():
    actual = _optimized("constant_fold.src").strip()
    expected = (VALID_DIR / "constant_fold.expected").read_text(encoding="utf-8").strip()
    assert actual == expected

def test_dead_code_elimination():
    actual = _optimized("dead_code.src").strip()
    expected = (VALID_DIR / "dead_code.expected").read_text(encoding="utf-8").strip()
    assert actual == expected

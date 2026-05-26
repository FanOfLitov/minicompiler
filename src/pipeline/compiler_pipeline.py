from pathlib import Path

from src.lexer.scanner import Scanner
from src.parser.parser import Parser
from src.semantic.analyzer import SemanticAnalyzer
from src.ir.ir_generator import IRGenerator
from src.codegen.x86_generator import X86Generator
from src.pipeline.build_config import BuildConfig
from src.pipeline.build_result import BuildResult
from src.pipeline.toolchain import Toolchain, ToolchainError

try:
    from src.optimizer.optimizer import IROptimizer
except Exception:
    IROptimizer = None


class CompilerPipeline:
    def __init__(self, toolchain=None):
        self.toolchain = toolchain or Toolchain()

    def compile(self, config: BuildConfig):
        config.output_dir.mkdir(parents=True, exist_ok=True)
        source = Path(config.input_file).read_text(encoding="utf-8")

        tokens = self._lex(source, str(config.input_file))
        if isinstance(tokens, BuildResult):
            return tokens

        ast = self._parse(tokens)
        if isinstance(ast, BuildResult):
            return ast

        semantic = self._semantic(ast, source, str(config.input_file))
        if isinstance(semantic, BuildResult):
            return semantic

        ir_program = IRGenerator().generate(ast)

        if config.optimize:
            if IROptimizer is None:
                result = BuildResult(False, "optimize")
                result.add_diagnostic("optimizer module is unavailable")
                return result
            ir_program = IROptimizer().optimize(ir_program)

        result = BuildResult(True, "codegen")

        if config.emit_ir:
            config.ir_path.write_text(ir_program.dump() + "\n", encoding="utf-8")
            result.add_artifact("ir", config.ir_path)

        asm = X86Generator().generate(ir_program)

        if config.emit_asm:
            config.asm_path.write_text(asm + "\n", encoding="utf-8")
            result.add_artifact("asm", config.asm_path)

        if config.assemble:
            try:
                code, out = self.toolchain.assemble(config.asm_path, config.obj_path)
                if code != 0:
                    fail = BuildResult(False, "assemble", result.artifacts[:])
                    fail.add_diagnostic(out.strip() or "assembler failed")
                    return fail
                result.add_artifact("object", config.obj_path)
            except ToolchainError as exc:
                fail = BuildResult(False, "assemble", result.artifacts[:])
                fail.add_diagnostic(str(exc))
                return fail

        if config.link:
            try:
                code, out = self.toolchain.link(config.obj_path, config.exe_path)
                if code != 0:
                    fail = BuildResult(False, "link", result.artifacts[:])
                    fail.add_diagnostic(out.strip() or "linker failed")
                    return fail
                result.add_artifact("executable", config.exe_path)
            except ToolchainError as exc:
                fail = BuildResult(False, "link", result.artifacts[:])
                fail.add_diagnostic(str(exc))
                return fail

        return result

    def _lex(self, source, filename):
        scanner = Scanner(source, filename=filename)
        tokens = scanner.scan_tokens() if hasattr(scanner, "scan_tokens") else scanner.scan_all()
        if scanner.errors:
            result = BuildResult(False, "lex")
            for err in scanner.errors:
                result.add_diagnostic(str(err))
            return result
        return tokens

    def _parse(self, tokens):
        parser = Parser(tokens)
        ast = parser.parse()
        if ast is None or parser.errors:
            result = BuildResult(False, "parse")
            for err in parser.errors:
                result.add_diagnostic(str(err))
            return result
        return ast

    def _semantic(self, ast, source, filename):
        analyzer = SemanticAnalyzer(filename=Path(filename).name, source=source)
        ok = analyzer.analyze(ast)
        if not ok:
            result = BuildResult(False, "semantic")
            result.add_diagnostic(analyzer.format_errors())
            return result
        return analyzer

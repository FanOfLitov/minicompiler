"""
Sprint 7 advanced local optimization passes.
Compatible with Python 3.8+.
"""
from dataclasses import dataclass
from typing import Dict, List

from src.ir.basic_block import IRProgram
from src.ir.ir_instructions import IRInstruction


@dataclass
class OptimizerStats:
    constant_propagated: int = 0
    algebraic_simplified: int = 0


class ConstantPropagator:
    def __init__(self):
        self.stats = OptimizerStats()

    def optimize(self, program: IRProgram):
        for function in program.functions.values():
            for block in function.blocks:
                known: Dict[str, str] = {}
                result: List[IRInstruction] = []

                for instr in block.instructions:
                    if instr.opcode == "STORE" and len(instr.args) == 2:
                        name, value = instr.args
                        if self._is_constant(value):
                            known[name] = value
                        else:
                            known.pop(name, None)
                        result.append(instr)
                        continue

                    if instr.opcode == "LOAD" and len(instr.args) == 1:
                        name = instr.args[0]
                        if name in known:
                            result.append(
                                IRInstruction(
                                    opcode="MOVE",
                                    dest=instr.dest,
                                    args=[known[name]],
                                    comment="constant propagated",
                                )
                            )
                            self.stats.constant_propagated += 1
                        else:
                            result.append(instr)
                        continue

                    result.append(instr)

                block.instructions = result

        return program

    def _is_constant(self, value):
        if value in ("true", "false"):
            return True
        if value.startswith("-"):
            return value[1:].isdigit()
        return value.isdigit()


class AlgebraicSimplifier:
    def __init__(self):
        self.stats = OptimizerStats()

    def optimize(self, program: IRProgram):
        for function in program.functions.values():
            for block in function.blocks:
                result = []

                for instr in block.instructions:
                    simplified = self._simplify(instr)
                    if simplified is not instr:
                        self.stats.algebraic_simplified += 1
                    result.append(simplified)

                block.instructions = result

        return program

    def _simplify(self, instr):
        if len(instr.args) != 2:
            return instr

        left, right = instr.args

        if instr.opcode == "ADD":
            if right == "0":
                return IRInstruction("MOVE", dest=instr.dest, args=[left], comment="algebraic simplified")
            if left == "0":
                return IRInstruction("MOVE", dest=instr.dest, args=[right], comment="algebraic simplified")

        if instr.opcode == "SUB":
            if right == "0":
                return IRInstruction("MOVE", dest=instr.dest, args=[left], comment="algebraic simplified")

        if instr.opcode == "MUL":
            if right == "1":
                return IRInstruction("MOVE", dest=instr.dest, args=[left], comment="algebraic simplified")
            if left == "1":
                return IRInstruction("MOVE", dest=instr.dest, args=[right], comment="algebraic simplified")
            if left == "0" or right == "0":
                return IRInstruction("MOVE", dest=instr.dest, args=["0"], comment="algebraic simplified")

        return instr


class Sprint7Optimizer:
    def __init__(self):
        self.constant_propagator = ConstantPropagator()
        self.algebraic_simplifier = AlgebraicSimplifier()

    def optimize(self, program: IRProgram):
        program = self.constant_propagator.optimize(program)
        program = self.algebraic_simplifier.optimize(program)
        return program

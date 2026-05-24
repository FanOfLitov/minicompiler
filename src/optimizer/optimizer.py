from .constant_folding import ConstantFolder
from .dead_code import DeadCodeEliminator

class IROptimizer:
    def __init__(self):
        self.cf = ConstantFolder()
        self.dce = DeadCodeEliminator()

    def optimize(self, program):
        program = self.cf.optimize(program)
        program = self.dce.optimize(program)
        return program

from collections import defaultdict

from src.ssa.ssa_ir import SSAProgram, SSAFunction, SSAInstruction


class SSABuilder:
    def __init__(self):
        self.temp_versions = defaultdict(int)
        self.var_versions = defaultdict(int)
        self.var_current = {}
        self.temp_current = {}

    def build(self, ir_program):
        ssa = SSAProgram()

        for ir_function in ir_program.functions.values():
            self.temp_versions.clear()
            self.var_versions.clear()
            self.var_current.clear()
            self.temp_current.clear()

            ssa_function = SSAFunction(
                ir_function.name,
                ir_function.return_type,
                list(ir_function.params),
            )

            for block in ir_function.blocks:
                ssa_block = ssa_function.new_block(block.label)

                for instr in block.instructions:
                    ssa_block.add(self._convert(instr))

            ssa.add_function(ssa_function)

        return ssa

    def _convert(self, instr):
        if instr.opcode == "LOAD":
            source = instr.args[0]
            current = self.var_current.get(source, source)
            dest = self._new_temp(instr.dest)
            return SSAInstruction(
                "MOVE",
                dest=dest,
                args=[current],
                comment="ssa load",
            )

        if instr.opcode == "STORE":
            name = instr.args[0]
            value = self._resolve(instr.args[1])
            versioned = self._new_var(name)
            self.var_current[name] = versioned
            return SSAInstruction(
                "MOVE",
                dest=versioned,
                args=[value],
                comment="ssa store",
            )

        if instr.opcode == "CALL":
            args = []
            if instr.args:
                args.append(instr.args[0])
                args.extend(self._resolve(a) for a in instr.args[1:])

            dest = self._new_temp(instr.dest) if instr.dest else None
            return SSAInstruction("CALL", dest=dest, args=args, comment=instr.comment)

        if instr.opcode in ("JUMP", "DECLARE"):
            return SSAInstruction(instr.opcode, args=list(instr.args), comment=instr.comment)

        if instr.opcode in ("JUMP_IF", "JUMP_IF_NOT"):
            return SSAInstruction(
                instr.opcode,
                args=[self._resolve(instr.args[0]), instr.args[1]],
                comment=instr.comment,
            )

        if instr.opcode == "RETURN":
            return SSAInstruction(
                "RETURN",
                args=[self._resolve(a) for a in instr.args],
                comment=instr.comment,
            )

        dest = self._new_temp(instr.dest) if instr.dest else None
        return SSAInstruction(
            instr.opcode,
            dest=dest,
            args=[self._resolve(a) for a in instr.args],
            comment=instr.comment,
        )

    def _new_temp(self, name):
        if not name:
            return name

        self.temp_versions[name] += 1
        versioned = "{}_{}".format(name, self.temp_versions[name])
        self.temp_current[name] = versioned
        return versioned

    def _new_var(self, name):
        self.var_versions[name] += 1
        return "{}.{}".format(name, self.var_versions[name])

    def _resolve(self, value):
        if value in self.temp_current:
            return self.temp_current[value]

        if value in self.var_current:
            return self.var_current[value]

        return value

import shutil
import subprocess


class ToolchainError(RuntimeError):
    pass


class Toolchain:
    def __init__(self, nasm="nasm", gcc="gcc"):
        self.nasm = nasm
        self.gcc = gcc

    def has_nasm(self):
        return shutil.which(self.nasm) is not None

    def has_gcc(self):
        return shutil.which(self.gcc) is not None

    def check(self):
        missing = []
        if not self.has_nasm():
            missing.append(self.nasm)
        if not self.has_gcc():
            missing.append(self.gcc)
        return missing

    def assemble(self, asm_path, obj_path):
        if not self.has_nasm():
            raise ToolchainError("NASM was not found")
        return self._run([self.nasm, "-felf64", str(asm_path), "-o", str(obj_path)])

    def link(self, obj_path, exe_path):
        if not self.has_gcc():
            raise ToolchainError("GCC was not found")
        return self._run([self.gcc, str(obj_path), "-o", str(exe_path)])

    def _run(self, cmd):
        completed = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )
        return completed.returncode, completed.stdout

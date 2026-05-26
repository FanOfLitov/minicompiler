from dataclasses import dataclass
from pathlib import Path


@dataclass
class BuildConfig:
    input_file: Path
    output_dir: Path
    output_name: str = "a.out"
    optimize: bool = False
    emit_ir: bool = True
    emit_asm: bool = True
    assemble: bool = False
    link: bool = False

    @property
    def stem(self):
        return Path(self.input_file).stem

    @property
    def ir_path(self):
        return self.output_dir / (self.stem + ".ir")

    @property
    def asm_path(self):
        return self.output_dir / (self.stem + ".asm")

    @property
    def obj_path(self):
        return self.output_dir / (self.stem + ".o")

    @property
    def exe_path(self):
        return self.output_dir / self.output_name

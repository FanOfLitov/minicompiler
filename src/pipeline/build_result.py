from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class BuildArtifact:
    kind: str
    path: Path


@dataclass
class BuildResult:
    success: bool
    stage: str
    artifacts: List[BuildArtifact] = field(default_factory=list)
    diagnostics: List[str] = field(default_factory=list)

    def add_artifact(self, kind, path):
        self.artifacts.append(BuildArtifact(kind, path))

    def add_diagnostic(self, message):
        self.diagnostics.append(message)

    def summary(self):
        lines = [
            "Build status: {}".format("success" if self.success else "failed"),
            "Last stage: {}".format(self.stage),
        ]

        if self.artifacts:
            lines.append("")
            lines.append("Artifacts:")
            for artifact in self.artifacts:
                lines.append("  {}: {}".format(artifact.kind, artifact.path))

        if self.diagnostics:
            lines.append("")
            lines.append("Diagnostics:")
            for diagnostic in self.diagnostics:
                lines.append("  - {}".format(diagnostic))

        return "\n".join(lines)

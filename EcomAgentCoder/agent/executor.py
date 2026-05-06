import subprocess
import sys
from pathlib import Path
from dataclasses import dataclass


@dataclass
class ExecutionResult:
    success: bool
    return_code: int
    stdout: str
    stderr: str


class Executor:
    def __init__(self, project_root: Path):
        self.project_root = project_root

    def run_pytest(self) -> ExecutionResult:
        command = [sys.executable, "-m", "pytest", "-q"]

        process = subprocess.run(
            command,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        return ExecutionResult(
            success=process.returncode == 0,
            return_code=process.returncode,
            stdout=process.stdout,
            stderr=process.stderr,
        )
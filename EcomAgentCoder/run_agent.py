
from pathlib import Path

from agent.workflow import AgenticCodingWorkflow


def main():
    root = Path(__file__).resolve().parent
    backend_root = root / "backend"
    prompt_path = root / "demo_prompt.md"

    if not backend_root.exists():
        raise RuntimeError(f"backend directory not found: {backend_root}")

    if not prompt_path.exists():
        raise RuntimeError(f"demo_prompt.md not found: {prompt_path}")

    requirement = prompt_path.read_text(encoding="utf-8")

    workflow = AgenticCodingWorkflow(
        project_root=backend_root,
        max_debug_rounds=2,
    )
    success = workflow.run(requirement)

    if not success:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
import json
import re
from pathlib import Path
from typing import Dict, Any


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def safe_project_path(project_root: Path, relative_path: str) -> Path:
    """
    防止意外写入项目之外的位置
    """
    clean = relative_path.replace("\\", "/").lstrip("/")
    target = (project_root / clean).resolve()
    root = project_root.resolve()

    if not str(target).startswith(str(root)):
        raise ValueError(f"Unsafe path: {relative_path}")

    return target


def extract_json(text: str) -> Dict[str, Any]:
    """
    从大模型输出内容中提取 JSON 对象
    """
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", text, flags=re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM output.")

    return json.loads(match.group(0))


def extract_file_blocks(text: str) -> Dict[str, str]:
    """
    提取以下格式的代码块：

    <<<FILE:app/routers/refund.py>>>
    ```python
    ...
    ```
    <<<END_FILE>>>
    """
    pattern = r"<<<FILE:(.*?)>>>\s*(?:```(?:python)?\s*)?(.*?)(?:```)?\s*<<<END_FILE>>>"
    matches = re.findall(pattern, text, flags=re.DOTALL)

    files = {}
    for path, content in matches:
        files[path.strip()] = content.strip() + "\n"

    return files


def snapshot_files(project_root: Path, relative_paths: list[str]) -> str:
    parts = []
    for rel in relative_paths:
        path = project_root / rel
        if path.exists():
            parts.append(f"\n===== {rel} =====\n{read_text(path)}")
        else:
            parts.append(f"\n===== {rel} =====\n<FILE_NOT_EXISTS>")
    return "\n".join(parts)


def print_section(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)
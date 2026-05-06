from pathlib import Path
from typing import Dict

from agent.llm_client import LLMClient
from agent.prompts import DEBUG_SYSTEM_PROMPT
from agent.utils import (
    extract_file_blocks,
    safe_project_path,
    snapshot_files,
    write_text,
)


class DebugAgent:
    def __init__(self, llm: LLMClient, project_root: Path):
        self.llm = llm
        self.project_root = project_root

    def run(self, pytest_stdout: str, pytest_stderr: str) -> Dict[str, str]:
        context = snapshot_files(
            self.project_root,
            [
                "app/main.py",
                "app/routers/refund.py",
                "app/services/refund_service.py",
                "tests/test_refund_api.py",
            ],
        )

        user_prompt = f"""
pytest 测试失败，请根据错误日志修复代码。

错误日志 stdout：
{pytest_stdout}

错误日志 stderr：
{pytest_stderr}

当前相关代码：
{context}

修复要求：
1. 只修改 app/main.py、app/routers/refund.py、app/services/refund_service.py、tests/test_refund_api.py。
2. 不允许修改 order.py 和 logistics.py。
3. 输出需要修改文件的完整内容。
4. 修复后 pytest 应该通过。
"""

        try:
            output = self.llm.chat(
                system_prompt=DEBUG_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.1,
            )
            files = extract_file_blocks(output)
            if not files:
                raise ValueError("No debug file blocks returned by LLM.")
        except Exception as exc:
            print(f"[DebugAgent] LLM failed, using fallback repair. Error: {exc}")
            files = self.fallback_files()

        allowed = {
            "app/main.py",
            "app/routers/refund.py",
            "app/services/refund_service.py",
            "tests/test_refund_api.py",
        }

        for rel_path, content in files.items():
            normalized = rel_path.replace("\\", "/")
            if normalized not in allowed:
                print(f"[DebugAgent] Skip unexpected file: {rel_path}")
                continue

            target = safe_project_path(self.project_root, normalized)
            write_text(target, content)
            print(f"[DebugAgent] Repaired {normalized}")

        return files

    @staticmethod
    def fallback_files() -> Dict[str, str]:
        return {
            "backend/app/main.py": '''from fastapi import FastAPI
from app.routers import order, logistics, refund

app = FastAPI(title="Ecom Customer Service API")

app.include_router(order.router, prefix="/api")
app.include_router(logistics.router, prefix="/api")
app.include_router(refund.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
''',
            "app/routers/refund.py": '''from fastapi import APIRouter, HTTPException
from app.services.refund_service import get_refund_by_order_id

router = APIRouter(prefix="/refund", tags=["Refund"])


@router.get("/{order_id}")
def get_refund(order_id: str):
    result = get_refund_by_order_id(order_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return result
''',
            "app/services/refund_service.py": '''from app.services.order_data import ORDERS

REFUNDS = {
    "10001": {
        "order_id": "10001",
        "refund_status": "processing",
        "refund_amount": 88.0,
        "estimated_arrival": "3个工作日",
    },
    "10003": {
        "order_id": "10003",
        "refund_status": "success",
        "refund_amount": 299.0,
        "estimated_arrival": "已到账",
    },
}


def get_refund_by_order_id(order_id: str):
    if order_id not in ORDERS:
        return None

    if order_id not in REFUNDS:
        return {
            "order_id": order_id,
            "refund_status": "none",
            "refund_amount": 0.0,
            "estimated_arrival": "",
        }

    return REFUNDS[order_id]
''',
            "tests/test_refund_api.py": '''from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_refund_success():
    response = client.get("/api/refund/10001")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "10001"
    assert data["refund_status"] == "processing"
    assert data["refund_amount"] == 88.0
    assert data["estimated_arrival"] == "3个工作日"


def test_refund_none():
    response = client.get("/api/refund/10002")
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "10002"
    assert data["refund_status"] == "none"
    assert data["refund_amount"] == 0.0
    assert data["estimated_arrival"] == ""


def test_refund_order_not_found():
    response = client.get("/api/refund/99999")
    assert response.status_code == 404


def test_refund_response_fields():
    response = client.get("/api/refund/10001")
    assert response.status_code == 200
    data = response.json()
    assert set(data.keys()) == {
        "order_id",
        "refund_status",
        "refund_amount",
        "estimated_arrival",
    }


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
''',
        }
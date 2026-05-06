from pathlib import Path
from typing import Dict, Any

from agent.llm_client import LLMClient
from agent.prompts import TESTER_SYSTEM_PROMPT
from agent.utils import extract_file_blocks, safe_project_path, write_text, snapshot_files


class TesterAgent:
    def __init__(self, llm: LLMClient, project_root: Path):
        self.llm = llm
        self.project_root = project_root

    def run(self, plan: Dict[str, Any], requirement: str) -> Dict[str, str]:
        context = snapshot_files(
            self.project_root,
            [
                "app/main.py",
                "app/routers/refund.py",
                "app/services/refund_service.py",
            ],
        )

        user_prompt = f"""
请为退款接口生成 pytest 测试文件。

原始需求：
{requirement}

开发计划：
{plan}

当前代码：
{context}

测试要求：
1. GET /api/refund/10001 应返回 200，refund_status 为 processing。
2. GET /api/refund/10002 应返回 200，refund_status 为 none。
3. GET /api/refund/99999 应返回 404。
4. 检查返回字段包含 order_id、refund_status、refund_amount、estimated_arrival。
5. GET /health 应返回 status=ok。

只输出 tests/test_refund_api.py。
"""

        try:
            output = self.llm.chat(
                system_prompt=TESTER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.1,
            )
            files = extract_file_blocks(output)
            if not files:
                raise ValueError("No test file block returned by LLM.")
        except Exception as exc:
            print(f"[TesterAgent] LLM failed, using fallback tests. Error: {exc}")
            files = self.fallback_files()

        allowed = {"tests/test_refund_api.py"}

        for rel_path, content in files.items():
            normalized = rel_path.replace("\\", "/")
            if normalized not in allowed:
                print(f"[TesterAgent] Skip unexpected file: {rel_path}")
                continue

            target = safe_project_path(self.project_root, normalized)
            write_text(target, content)
            print(f"[TesterAgent] Wrote {normalized}")

        return files

    @staticmethod
    def fallback_files() -> Dict[str, str]:
        return {
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
'''
        }
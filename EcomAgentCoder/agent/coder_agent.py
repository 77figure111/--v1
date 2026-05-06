from pathlib import Path
from typing import Dict, Any

from agent.llm_client import LLMClient
from agent.prompts import CODER_SYSTEM_PROMPT
from agent.utils import extract_file_blocks, safe_project_path, write_text, snapshot_files


class CoderAgent:
    def __init__(self, llm: LLMClient, project_root: Path):
        self.llm = llm
        self.project_root = project_root

    def run(self, plan: Dict[str, Any], requirement: str) -> Dict[str, str]:
        context = snapshot_files(
            self.project_root,
            [
                "app/main.py",
                "app/routers/order.py",
                "app/routers/logistics.py",
                "app/services/order_data.py",
            ],
        )

        user_prompt = f"""
请根据开发计划为当前 FastAPI 项目生成代码。

原始需求：
{requirement}

开发计划：
{plan}

当前项目关键文件：
{context}

你需要输出这些文件的完整内容：
1. app/routers/refund.py
2. app/services/refund_service.py
3. app/main.py

注意：
- app/main.py 要注册 refund router。
- refund_service.py 可以复用 app.services.order_data 中的 ORDERS。
- 订单不存在时，接口应返回 404。
- 订单存在但没有退款记录时，返回 refund_status = "none"。
- 不要修改 order.py 和 logistics.py。
"""

        try:
            output = self.llm.chat(
                system_prompt=CODER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.1,
            )
            files = extract_file_blocks(output)
            if not files:
                raise ValueError("No file blocks returned by LLM.")
        except Exception as exc:
            print(f"[CoderAgent] LLM failed, using fallback code. Error: {exc}")
            files = self.fallback_files()

        allowed = {
            "app/routers/refund.py",
            "app/services/refund_service.py",
            "app/main.py",
        }

        for rel_path, content in files.items():
            normalized = rel_path.replace("\\", "/")
            if normalized not in allowed:
                print(f"[CoderAgent] Skip unexpected file: {rel_path}")
                continue

            target = safe_project_path(self.project_root, normalized)
            write_text(target, content)
            print(f"[CoderAgent] Wrote {normalized}")

        return files

    @staticmethod
    def fallback_files() -> Dict[str, str]:
        return {
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
            "app/main.py": '''from fastapi import FastAPI
from app.routers import order, logistics, refund

app = FastAPI(title="Ecom Customer Service API")

app.include_router(order.router, prefix="/api")
app.include_router(logistics.router, prefix="/api")
app.include_router(refund.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}
''',
        }
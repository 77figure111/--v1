
from typing import Dict, Any

from agent.llm_client import LLMClient
from agent.prompts import PLANNER_SYSTEM_PROMPT
from agent.utils import extract_json


class PlannerAgent:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def run(self, requirement: str) -> Dict[str, Any]:
        user_prompt = f"""
    请将下面的开发需求拆解为 JSON 开发计划。
    
    需求：
    {requirement}
    
    你必须输出如下 JSON 结构：
    
    {{
      "task_name": "新增退款状态查询接口",
      "api": {{
        "method": "GET",
        "path": "/api/refund/{{order_id}}"
      }},
      "files_to_create": [
        "app/routers/refund.py",
        "app/services/refund_service.py",
        "tests/test_refund_api.py"
      ],
      "files_to_modify": [
        "app/main.py"
      ],
      "business_rules": [
        "订单存在且有退款记录时返回退款信息",
        "订单存在但没有退款记录时返回 refund_status=none",
        "订单不存在时返回 404"
      ],
      "test_cases": [
        "有退款记录的订单",
        "无退款记录的订单",
        "不存在的订单",
        "返回字段完整性",
        "health check"
      ],
      "constraints": [
        "不允许修改 app/routers/order.py",
        "不允许修改 app/routers/logistics.py",
        "pytest 必须通过"
      ]
    }}
    """
        try:
            output = self.llm.chat(
                system_prompt=PLANNER_SYSTEM_PROMPT,
                user_prompt=user_prompt,
                temperature=0.1,
            )
            return extract_json(output)
        except Exception as exc:
            print(f"[PlannerAgent] LLM failed, using fallback plan. Error: {exc}")
            return self.fallback_plan()

    @staticmethod
    def fallback_plan() -> Dict[str, Any]:
        return {
            "task_name": "新增退款状态查询接口",
            "api": {
                "method": "GET",
                "path": "/api/refund/{order_id}",
            },
            "files_to_create": [
                "app/routers/refund.py",
                "app/services/refund_service.py",
                "tests/test_refund_api.py",
            ],
            "files_to_modify": [
                "app/main.py",
            ],
            "business_rules": [
                "订单存在且有退款记录时返回退款信息",
                "订单存在但没有退款记录时返回 refund_status=none",
                "订单不存在时返回 404",
            ],
            "test_cases": [
                "有退款记录的订单",
                "无退款记录的订单",
                "不存在的订单",
                "返回字段完整性",
                "health check",
            ],
            "constraints": [
                "不允许修改 app/routers/order.py",
                "不允许修改 app/routers/logistics.py",
                "pytest 必须通过",
            ],
        }
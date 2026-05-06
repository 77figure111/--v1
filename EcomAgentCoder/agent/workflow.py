from pathlib import Path
from datetime import datetime

from agent.llm_client import LLMClient
from agent.planner_agent import PlannerAgent
from agent.coder_agent import CoderAgent
from agent.tester_agent import TesterAgent
from agent.executor import Executor
from agent.debug_agent import DebugAgent
from agent.utils import print_section, write_text


class AgenticCodingWorkflow:
    def __init__(self, project_root: Path, max_debug_rounds: int = 2):
        self.project_root = project_root
        self.max_debug_rounds = max_debug_rounds

        self.llm = LLMClient()
        self.planner = PlannerAgent(self.llm)
        self.coder = CoderAgent(self.llm, project_root)
        self.tester = TesterAgent(self.llm, project_root)
        self.executor = Executor(project_root)
        self.debugger = DebugAgent(self.llm, project_root)

    def run(self, requirement: str) -> bool:
        print_section("1. PlannerAgent: 需求拆解")
        plan = self.planner.run(requirement)
        print(plan)

        print_section("2. CoderAgent: 生成接口代码")
        self.coder.run(plan, requirement)

        print_section("3. TestEngineerAgent: 生成测试代码")
        self.tester.run(plan, requirement)

        print_section("4. VerifierAgent: 执行 pytest")
        result = self.executor.run_pytest()
        print(result.stdout)
        if result.stderr:
            print(result.stderr)

        debug_round = 0
        while not result.success and debug_round < self.max_debug_rounds:
            debug_round += 1
            print_section(f"5. DebuggerAgent: 第 {debug_round} 轮修复")
            self.debugger.run(result.stdout, result.stderr)

            print_section(f"6. VerifierAgent: 第 {debug_round} 轮修复后重新测试")
            result = self.executor.run_pytest()
            print(result.stdout)
            if result.stderr:
                print(result.stderr)

        print_section("7. 生成验证报告")
        self._write_report(requirement, plan, result)

        if result.success:
            print("✅ Agentic Coding Demo 成功：pytest 已通过。")
        else:
            print("❌ Agentic Coding Demo 未完全通过：请查看 pytest 日志。")

        return result.success

    def _write_report(self, requirement: str, plan: dict, result) -> None:
        report = f"""# EcomAgentCoder 验证报告

        生成时间：{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        
        ## 1. 原始需求
        
        {requirement}
        
        ## 2. Agent 开发计划
        
        ```json
        {plan}
        ## 3. 多智能体流程
        PlannerAgent：拆解需求，生成开发计划。
        CoderAgent：生成 FastAPI 路由、业务逻辑并修改 main.py。
        TestEngineerAgent：生成 pytest 测试用例。
        VerifierAgent：运行 pytest 验证。
        DebuggerAgent：若测试失败，根据错误日志修复代码。
        ## 4. 测试结果
        
        return_code: {result.return_code}
        
        stdout:
        
        {result.stdout}
        
        stderr:
        
        {result.stderr}
        ## 5. 结论
        
        {"测试全部通过，说明从需求理解、代码生成、测试生成到结果验证的 Agentic Coding 闭环已跑通。" 
                if result.success 
                else "测试未全部通过，需要继续修复。"}
        """
        write_text(self.project_root.parent / "validation_report.md", report)
        print("已生成 validation_report.md")
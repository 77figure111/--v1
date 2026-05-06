# Agentic Coding 工作流


1. 输入需求
用户输入自然语言需求：

请为当前电商客服 FastAPI 项目新增退款状态查询接口 GET /api/refund/{order_id}
2. 需求拆解

PlannerAgent 将需求拆解为结构化 JSON，包括接口路径、业务规则、文件修改范围和测试用例。

3. 代码生成

CoderAgent 根据开发计划生成以下文件：

app/routers/refund.py
app/services/refund_service.py
app/main.py
4. 测试生成

TestEngineerAgent 生成：

tests/test_refund_api.py
5. 自动验证

VerifierAgent 执行：

python -m pytest -q
6. 失败修复

如果测试失败，DebuggerAgent 读取 pytest 错误日志并修复代码。

7. 最终结果

最终 pytest 结果：

5 passed
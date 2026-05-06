# 多智能体角色设计

## PlannerAgent

PlannerAgent 负责理解自然语言需求，并将其拆解为结构化开发计划，包括接口路径、请求方法、需要创建和修改的文件、业务规则、测试用例和约束条件。

## CoderAgent

CoderAgent 根据 PlannerAgent 的开发计划生成 FastAPI 路由代码和业务逻辑代码。在本项目中，它负责生成 `refund.py`、`refund_service.py`，并修改 `main.py` 注册退款接口。

## TestEngineerAgent

TestEngineerAgent 负责根据接口规范生成 pytest 测试用例，覆盖正常订单、无退款订单、不存在订单和字段完整性检查。

## VerifierAgent

VerifierAgent 负责执行 pytest，并收集测试输出、错误日志和返回码，用于判断本轮代码生成是否成功。

## DebuggerAgent

DebuggerAgent 在测试失败时启动。它读取 pytest 错误日志，定位失败原因，并对相关代码进行最小范围修复。修复后重新交由 VerifierAgent 验证。
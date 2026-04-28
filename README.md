# --v1 ---EcomAgentCoder：面向电商客服系统的 Agentic Coding 助手
用户输入需求
  ↓
PlannerAgent 生成开发计划
  ↓
CoderAgent 生成 FastAPI 接口代码
  ↓
TesterAgent 生成 pytest 测试
  ↓
Executor 自动运行 pytest
  ↓
如果失败，DebuggerAgent 根据报错修复
  ↓
输出验证报告

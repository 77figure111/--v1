# EcomAgentCoder

EcomAgentCoder 是一个面向电商客服系统的轻量级 Agentic Coding 。

项目目标是：根据自然语言需求，自动完成 FastAPI 业务接口代码生成、测试用例生成、pytest 验证和错误修复。

## 1. 项目背景

电商客服系统经常需要新增订单查询、物流查询、退款状态查询等业务接口。传统开发流程需要开发者手动理解需求、编写代码、补充测试并反复调试。

本项目使用多智能体协同方式，将需求分析、代码生成、测试生成和错误修复串联为一个自动化闭环。

## 2. 多智能体设计

| Agent | 职责 |
|---|---|
| PlannerAgent | 分析自然语言需求，生成开发计划 |
| CoderAgent | 生成 FastAPI 接口代码和业务逻辑 |
| TestEngineerAgent | 生成 pytest 测试用例 |
| VerifierAgent | 运行 pytest 并捕获日志 |
| DebuggerAgent | 根据错误日志修复代码 |

## 3. 任务

新增退款状态查询接口：

GET /api/refund/{order_id}

业务规则：

1. 有退款记录时返回退款状态、金额和到账时间。
2. 无退款记录时返回 refund_status = none。
3. 订单不存在时返回 404。
4. 自动生成测试并通过 pytest。

## 4. 安装依赖

```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt



<img width="1241" height="338" alt="1" src="https://github.com/user-attachments/assets/d46be4c4-7f70-43ce-8b5e-03c6acf7f610" />
<img width="767" height="270" alt="2" src="https://github.com/user-attachments/assets/732ca57a-b1da-4bcc-b429-2786ed3a8d5f" />
<img width="781" height="458" alt="4" src="https://github.com/user-attachments/assets/d2c650c6-861a-4b0d-8857-b393a7baba12" />
<img width="715" height="124" alt="5" src="https://github.com/user-attachments/assets/13b1fc07-6e53-4aeb-8dbd-ecb2698ba2b0" />




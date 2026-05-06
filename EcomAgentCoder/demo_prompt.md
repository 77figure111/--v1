请为当前电商客服 FastAPI 项目新增退款状态查询功能。

业务接口：

GET /api/refund/{order_id}

返回字段：

- order_id: 订单号
- refund_status: 退款状态，包括 none、processing、success、failed
- refund_amount: 退款金额
- estimated_arrival: 预计到账时间

业务规则：

1. 如果订单存在退款记录，返回退款信息。
2. 如果订单存在但没有退款记录，返回 refund_status = "none"。
3. 如果订单不存在，返回 404。
4. 接口代码放在 app/routers/refund.py。
5. 退款业务逻辑放在 app/services/refund_service.py。
6. 需要修改 app/main.py 注册 refund router。
7. 需要生成 tests/test_refund_api.py。
8. 测试至少覆盖：
   - 有退款记录的订单
   - 无退款记录的订单
   - 不存在的订单
   - 返回字段完整性
   - health check

约束：

1. 不允许修改 order.py 和 logistics.py 的已有业务逻辑。
2. 不允许删除已有接口。
3. 所有测试必须通过 pytest。
4. 如果测试失败，需要根据错误日志修复。
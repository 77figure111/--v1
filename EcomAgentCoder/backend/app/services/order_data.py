ORDERS = {
    "10001": {
        "order_id": "10001",
        "status": "paid",
        "amount": 199.0,
        "customer": "张三",
    },
    "10002": {
        "order_id": "10002",
        "status": "shipped",
        "amount": 88.0,
        "customer": "李四",
    },
    "10003": {
        "order_id": "10003",
        "status": "delivered",
        "amount": 299.0,
        "customer": "王五",
    },
}


LOGISTICS = {
    "10001": {
        "order_id": "10001",
        "status": "in_transit",
        "location": "西安转运中心",
    },
    "10002": {
        "order_id": "10002",
        "status": "delivered",
        "location": "已签收",
    },
    "10003": {
        "order_id": "10003",
        "status": "pending",
        "location": "仓库待发货",
    },
}
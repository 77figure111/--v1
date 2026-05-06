from fastapi import APIRouter, HTTPException

from app.services.order_data import ORDERS

router = APIRouter(prefix="/order", tags=["Order"])


@router.get("/{order_id}")
def get_order(order_id: str):
    if order_id not in ORDERS:
        raise HTTPException(status_code=404, detail="Order not found")
    return ORDERS[order_id]
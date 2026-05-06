from fastapi import APIRouter, HTTPException

from app.services.order_data import LOGISTICS

router = APIRouter(prefix="/logistics", tags=["Logistics"])


@router.get("/{order_id}")
def get_logistics(order_id: str):
    if order_id not in LOGISTICS:
        raise HTTPException(status_code=404, detail="Logistics not found")
    return LOGISTICS[order_id]
from fastapi import FastAPI

from app.routers import order, logistics, refund

app = FastAPI(title="Ecom Customer Service API")

app.include_router(order.router, prefix="/api")
app.include_router(logistics.router, prefix="/api")
app.include_router(refund.router, prefix="/api")


@app.get("/health")
def health_check():
    return {"status": "ok"}

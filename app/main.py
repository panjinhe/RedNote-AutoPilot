from fastapi import FastAPI, HTTPException

from app.config.settings import get_settings
from app.models.schemas import ProductCreate
from app.workflows.auto_ops import AutoOpsWorkflow

app = FastAPI(title="RedNote-AutoPilot", version="0.2.0")
workflow = AutoOpsWorkflow()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/products/auto-create")
def auto_create_product(product: ProductCreate) -> dict:
    return workflow.product_manager.auto_create_product(product)


@app.get("/tasks/{task_id}")
def get_task(task_id: str) -> dict:
    return workflow.product_manager.get_task(task_id)


@app.post("/tasks/{task_id}/confirm")
def confirm_task(task_id: str) -> dict:
    try:
        return workflow.product_manager.confirm_task(task_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/ops/sales-loop")
def sales_loop() -> dict:
    return workflow.run_sales_loop()


@app.get("/ops/channel")
def channel_mode() -> dict:
    settings = get_settings()
    return {"operation_mode": settings.operation_mode}

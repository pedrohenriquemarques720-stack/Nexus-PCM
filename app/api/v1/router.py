from fastapi import APIRouter
from app.api.v1.endpoints import auth, assets, work_orders, metrics

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(work_orders.router, prefix="/work-orders", tags=["Work Orders"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["Metrics"])
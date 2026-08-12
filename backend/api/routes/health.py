from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/health", tags=["Health"])

@router.get("", summary="Health Check")
async def health_check():
    return {
        "status": "ok",
        "version": "1.0.0",
        "runtime": True,
        "storage": True,
        "database": True
    }

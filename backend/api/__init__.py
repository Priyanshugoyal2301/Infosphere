from fastapi import APIRouter
from .v1.endpoints import issues, media, policy

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(issues.router, prefix="/issues", tags=["Citizen Issues"])
api_router.include_router(media.router, prefix="/media", tags=["Media Integrity"])
api_router.include_router(policy.router, prefix="/policy", tags=["Policy Analysis"])

# Try to include ATIE router
try:
    from .v1.endpoints import atie
    api_router.include_router(atie.router, prefix="/atie", tags=["AI Trust & Integrity"])
    print("ATIE endpoints registered successfully")
except ImportError as e:
    print(f"Warning: ATIE router not available: {e}")
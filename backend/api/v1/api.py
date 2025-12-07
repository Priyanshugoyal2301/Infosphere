from fastapi import APIRouter
from .endpoints import issues, media, policy, news, auth, enhanced_verification

# Create main API router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(issues.router, prefix="/issues", tags=["Citizen Issues"])
api_router.include_router(media.router, prefix="/media", tags=["Media Integrity"])
api_router.include_router(policy.router, prefix="/policy", tags=["Policy Analysis"])
api_router.include_router(news.router, tags=["Real-time News"])
api_router.include_router(auth.router, tags=["Authentication"])
api_router.include_router(enhanced_verification.router, prefix="/enhanced-verification", tags=["Advanced Verification"])
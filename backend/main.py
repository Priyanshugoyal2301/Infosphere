from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
import sys
import os
import json
from dotenv import load_dotenv

# Add the backend directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Import after setting path
try:
    from database.database import init_db
except ImportError:
    print("Warning: Database module not available, using mock database")
    def init_db():
        print("Mock database initialized")

# Import API routers
try:
    from api.v1.endpoints.atie import router as atie_router
    atie_available = True
except ImportError as e:
    print(f"Warning: ATIE endpoints not available: {e}")
    atie_available = False

try:
    from api.v1.endpoints.news import router as news_router
    news_available = True
except ImportError as e:
    print(f"Warning: News router not available: {e}")
    news_available = False

try:
    from api.v1.endpoints.auth import router as auth_router
    auth_available = True
except ImportError as e:
    print(f"Warning: Auth router not available: {e}")
    auth_available = False

try:
    from api.v1.endpoints.issues import router as issues_router
    from api.v1.endpoints.media import router as media_router
    from api.v1.endpoints.policy import router as policy_router
    core_routers_available = True
except ImportError as e:
    print(f"Warning: Core routers not available: {e}")
    core_routers_available = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting Infosphere API...")
    
    # Initialize database
    try:
        init_db()
        print("✅ Database initialized successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
    
    # Initialize ML models (placeholder for now)
    print("🤖 ML models ready (using mock implementations)")
    
    # Initialize ATIE service
    if atie_available:
        try:
            print("🔍 Initializing ATIE (AI Trust and Integrity Engine)...")
            # ATIE service initializes automatically when imported
            print("✅ ATIE service ready for textual integrity analysis")
        except Exception as e:
            print(f"⚠️ ATIE initialization warning: {e}")
    
    yield
    
    # Shutdown
    print("🔄 Shutting down Infosphere API...")

# Create FastAPI application
app = FastAPI(
    title="Infosphere API",
    description="AI-Powered Civic Intelligence Platform",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
cors_origins_env = os.getenv("CORS_ORIGINS", "*")
cors_origins = [o.strip() for o in cors_origins_env.split(",") if o.strip()]

# If wildcard is used, credentials must be disabled per CORS spec
allow_credentials = "*" not in cors_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["localhost", "127.0.0.1", "*.localhost"]
)

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "Welcome to Infosphere API",
        "status": "healthy",
        "version": "1.0.0",
        "features": [
            "AI Media Integrity Engine (MIE)",
            "AI Trust and Integrity Engine (ATIE)", 
            "Citizen Issue Tracking", 
            "AI Policy Sensemaking"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Infosphere API is running"}

# Simple auth endpoints for testing
@app.post("/api/v1/auth/register")
async def register_endpoint(user_data: dict):
    """Simple registration endpoint"""
    import json
    import os
    from datetime import datetime
    import hashlib
    import secrets
    
    # Load or create users file
    users_file = "backend/data/users.json"
    os.makedirs(os.path.dirname(users_file), exist_ok=True)
    
    if os.path.exists(users_file):
        with open(users_file, 'r') as f:
            data = json.load(f)
    else:
        data = {"users": [], "sessions": {}, "metadata": {"total_users": 0}}
    
    # Check if username exists
    for user in data["users"]:
        if user["username"].lower() == user_data["username"].lower():
            raise HTTPException(status_code=400, detail="Username already exists")
    
    # Create new user
    user_id = f"user_{secrets.token_hex(4)}"
    hashed_password = hashlib.sha256(user_data["password"].encode()).hexdigest()
    
    new_user = {
        "id": user_id,
        "username": user_data["username"],
        "email": user_data["email"],
        "full_name": user_data["full_name"],
        "password_hash": hashed_password,
        "created_at": datetime.now().isoformat(),
        "last_login": None,
        "is_active": True
    }
    
    data["users"].append(new_user)
    data["metadata"]["total_users"] = len(data["users"])
    
    with open(users_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    return {
        "id": user_id,
        "username": new_user["username"],
        "email": new_user["email"],
        "full_name": new_user["full_name"],
        "created_at": new_user["created_at"]
    }

@app.post("/api/v1/auth/login")
async def login_endpoint(login_data: dict):
    """Simple login endpoint"""
    import json
    import os
    from datetime import datetime, timedelta
    import hashlib
    import secrets
    
    users_file = "backend/data/users.json"
    if not os.path.exists(users_file):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    with open(users_file, 'r') as f:
        data = json.load(f)
    
    hashed_password = hashlib.sha256(login_data["password"].encode()).hexdigest()
    
    for user in data["users"]:
        if (user["username"].lower() == login_data["username"].lower() and 
            user["password_hash"] == hashed_password and user["is_active"]):
            
            # Update last login
            user["last_login"] = datetime.now().isoformat()
            
            # Create session
            session_token = secrets.token_urlsafe(32)
            expires_at = (datetime.now() + timedelta(hours=24)).isoformat()
            
            data["sessions"][session_token] = {
                "user_id": user["id"],
                "username": user["username"],
                "created_at": datetime.now().isoformat(),
                "expires_at": expires_at,
                "is_active": True
            }
            
            with open(users_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return {
                "success": True,
                "user": {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "created_at": user["created_at"],
                    "last_login": user["last_login"]
                },
                "session_token": session_token,
                "message": "Login successful"
            }
    
    raise HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/api/v1/auth/health")
async def auth_health():
    """Auth service health check"""
    return {"status": "healthy", "service": "authentication", "version": "1.0.0"}

@app.get("/api/v1/auth/profile")
async def get_profile(authorization: str = Header(None)):
    """Get user profile information"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token required")
    
    token = authorization.split(" ")[1]
    
    # Import auth service here to avoid circular imports
    from services.auth_service import AuthService
    auth_service = AuthService()
    
    user_data = auth_service.validate_session(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    # Get full user details
    try:
        with open("data/users.json", "r") as f:
            data = json.load(f)
            
        for user in data["users"]:
            if user["id"] == user_data["user_id"]:
                return {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "created_at": user["created_at"],
                    "last_login": user["last_login"],
                    "is_active": user["is_active"]
                }
        
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to fetch profile")

@app.put("/api/v1/auth/profile")
async def update_profile(profile_data: dict, authorization: str = Header(None)):
    """Update user profile information"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token required")
    
    token = authorization.split(" ")[1]
    
    # Import auth service here to avoid circular imports
    from services.auth_service import AuthService
    auth_service = AuthService()
    
    user_data = auth_service.validate_session(token)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    # Update user profile
    try:
        with open("data/users.json", "r") as f:
            data = json.load(f)
            
        for user in data["users"]:
            if user["id"] == user_data["user_id"]:
                # Update allowed fields
                if "full_name" in profile_data:
                    user["full_name"] = profile_data["full_name"]
                if "email" in profile_data:
                    user["email"] = profile_data["email"]
                
                # Save updated data
                with open("data/users.json", "w") as f:
                    json.dump(data, f, indent=2)
                
                return {
                    "id": user["id"],
                    "username": user["username"],
                    "email": user["email"],
                    "full_name": user["full_name"],
                    "created_at": user["created_at"],
                    "last_login": user["last_login"],
                    "is_active": user["is_active"]
                }
        
        raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to update profile")

# Include API routers
if atie_available:
    app.include_router(atie_router, prefix="/api/v1")
    print("📡 ATIE API endpoints registered at /api/v1/atie/*")

if news_available:
    app.include_router(news_router, prefix="/api/v1")
    print("📰 News API endpoints registered at /api/v1/news/*")

if auth_available:
    app.include_router(auth_router, prefix="/api/v1")
    print("🔐 Auth API endpoints registered at /api/v1/auth/*")

if core_routers_available:
    app.include_router(issues_router, prefix="/api/v1")
    app.include_router(media_router, prefix="/api/v1")
    app.include_router(policy_router, prefix="/api/v1")
    print("✅ Core API endpoints registered at /api/v1/(issues|media|policy)/*")

# Remove old mock endpoints; real routers are now mounted.
# News endpoints are now provided by the news_router

# News endpoints are now provided by the news_router - inline endpoints removed

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
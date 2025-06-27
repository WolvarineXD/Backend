from fastapi import FastAPI
from routes.auth_routes import router as auth_router
from routes.jd_routes import router as jd_router
from fastapi.middleware.cors import CORSMiddleware

# 🔐 Add SlowAPI for rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse

# ✅ FastAPI App
app = FastAPI(
    title="Resume Shortlister API",
    description="Backend API for login, JD submission, and scoring",
    version="1.0.0"
)

# ✅ Rate Limiting Configuration
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Too many requests. Please try again later."}
    )

# ✅ CORS for Vercel frontend (no trailing slash)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://resume-filter1-6p92.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Include route modules
app.include_router(auth_router)
app.include_router(jd_router)

# ✅ Root health check endpoint
@app.get("/")
def root():
    return {"message": "Login/Signup backend running"}

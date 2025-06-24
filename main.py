from fastapi import FastAPI
from routes.auth_routes import router as auth_router
from routes.jd_routes import router as jd_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Resume Shortlister API",
    description="Backend API for login, JD submission, and scoring",
    version="1.0.0"
)

# ✅ Enable CORS for all origins (adjust in prod if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with frontend origin in production
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

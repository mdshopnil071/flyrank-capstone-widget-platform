from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.database import Base, engine
from app.config import settings
from app.routers import auth, widgets, public, dashboard
from app.routers.public import limiter

# Auto-generate database schema models in Supabase Postgres instance
Base.metadata.create_all(bind=engine)

app = FastAPI(title="FlyRank Lead-Capture Widget Platform", version="1.0.0")

@app.middleware("http")
async def request_size_guard(request: Request, call_next):
    content_length = request.headers.get("content-length")
    if content_length and int(content_length) > settings.MAX_BODY_BYTES:
        return JSONResponse(status_code=413, content={"detail": "Request payload is too large"})
    return await call_next(request)

# Attach Rate Limiter exception handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Enable universal embedding compatibility
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve versioned widget static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register application routers
app.include_router(auth.router)
app.include_router(widgets.router)
app.include_router(public.router)
app.include_router(dashboard.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}
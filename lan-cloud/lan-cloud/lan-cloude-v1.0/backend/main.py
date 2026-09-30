"""LAN Cloud API. Restrict network access with the host firewall."""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from .database import init_db
from .devices import router as devices_router
from .files import router as files_router

app = FastAPI(title="LAN Cloud", version="1.0.1", docs_url=None, redoc_url=None)

@app.on_event("startup")
def startup():
    init_db()

@app.exception_handler(Exception)
async def safe_error_handler(request: Request, exc: Exception):
    # Avoid leaking stack traces, local paths, or filesystem details to clients.
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})

@app.get("/")
def root():
    return {"name": "LAN Cloud", "version": app.version, "scope": "private LAN"}

@app.get("/health")
def health():
    return {"status": "ok", "version": app.version}

app.include_router(devices_router, prefix="/register", tags=["devices"])
app.include_router(files_router, tags=["files"])

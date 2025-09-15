from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import load_config


cfg = load_config()

app = FastAPI(title="Step1 RAG API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cfg.allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"status": "ok"}


# Routers will be included after they are implemented
try:
    from routes_ingest import router as ingest_router
    from routes_ask import router as ask_router
    from routes_admin import router as admin_router

    app.include_router(ingest_router)
    app.include_router(ask_router)
    app.include_router(admin_router)
except Exception:
    # During early scaffolding, routes may be missing; ignore.
    pass

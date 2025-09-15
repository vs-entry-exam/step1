from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import load_config


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


# Include essential routers (should not fail under tests)
from app.routers.rag import router as ingest_router
from app.routers.admin import router as admin_router

app.include_router(ingest_router)
app.include_router(admin_router)

# Include optional Agent router (guarded; relies on LangChain/OpenAI at runtime)
from app.routers.agent import router as agent_router

app.include_router(agent_router)

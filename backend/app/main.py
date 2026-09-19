from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import cases, sessions

app = FastAPI(
    title="OSCE Clinical Reasoning Simulator",
    description="Virtual standardized-patient stations for pre-med history taking.",
    version="0.1.0",
)

_allow_all = settings.cors_origins.strip() == "*"
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if _allow_all else settings.cors_origin_list,
    allow_credentials=not _allow_all,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cases.router)
app.include_router(sessions.router)


@app.get("/")
def root() -> dict[str, str]:
    return {"app": "OSCE Clinical Reasoning Simulator", "docs": "/docs"}


@app.get("/api/health")
def health() -> dict[str, str]:
    mode = "openai" if settings.openai_api_key.strip() else "mock"
    return {"status": "ok", "llm": mode}

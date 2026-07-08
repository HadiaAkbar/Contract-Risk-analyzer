from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app import models  # noqa: F401 - ensures models are registered before create_all
from app.routers import (
    auth_router, documents_router, search_router,
    reports_router, dashboard_router, admin_router,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI-Powered Contract & Legal Document Risk Analyzer",
    description="Upload contracts, get AI-driven clause extraction, risk detection, "
                "summaries, semantic search, and downloadable reports.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(documents_router.router)
app.include_router(search_router.router)
app.include_router(reports_router.router)
app.include_router(dashboard_router.router)
app.include_router(admin_router.router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "service": "contract-risk-analyzer"}

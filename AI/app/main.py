from fastapi import FastAPI

from app.core.config import settings
from app.routers import chat, cv_parser, generation, interview, jd_parser, matching, search


app = FastAPI(
    title=settings.service_name,
    debug=settings.debug,
    version="0.1.0",
)


@app.get("/health")
def health() -> dict:
    return {
        "success": True,
        "service": settings.service_name,
        "status": "ok",
        "local_llm_model": settings.local_llm_model,
    }


app.include_router(cv_parser.router, tags=["cv-parser"])
app.include_router(jd_parser.router, tags=["jd-parser"])
app.include_router(matching.router, tags=["matching"])
app.include_router(generation.router, tags=["generation"])
app.include_router(search.router, tags=["search"])
app.include_router(chat.router, tags=["chat"])
app.include_router(interview.router, tags=["interview"])

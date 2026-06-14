from fastapi import FastAPI

from app.api.analysis import router as analysis_router
from app.api.projects import router as projects_router

app = FastAPI(
    title="AI Legacy Modernization Platform",
    version="1.0.0"
)

app.include_router(projects_router)
app.include_router(analysis_router)


@app.get("/")
def health_check():
    return {
        "status": "running"
    }

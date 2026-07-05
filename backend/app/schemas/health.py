from pydantic import BaseModel, Field


class DependencyStatus(BaseModel):
    name: str
    status: str
    message: str | None = None


class HealthResponse(BaseModel):
    status: str = Field(..., examples=["healthy"])
    service: str
    version: str


class ReadinessResponse(BaseModel):
    status: str = Field(..., examples=["ready"])
    service: str
    version: str
    dependencies: list[DependencyStatus]

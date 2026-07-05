from datetime import datetime

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error_code: str = Field(
        ...,
        description="Machine-readable error identifier",
        examples=["VALIDATION_ERROR"],
    )
    message: str = Field(
        ...,
        description="Human-readable error message",
        examples=["Project not found"],
    )
    detail: str = Field(
        ...,
        description="Same as message; retained for backward compatibility",
    )
    timestamp: datetime = Field(
        ...,
        description="UTC timestamp when the error occurred",
    )
    path: str = Field(
        ...,
        description="Request path that triggered the error",
        examples=["/projects/1/analysis"],
    )

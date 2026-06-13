from pydantic import BaseModel


class UploadResponse(BaseModel):
    project_id: int
    status: str
    files_processed: int

from pydantic import BaseModel
from typing import Optional

class IngestionRequest(BaseModel):
    file_name: str
    folder: Optional[str] = None

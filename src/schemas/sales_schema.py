from pydantic import BaseModel, Field

class SalesRequest(BaseModel):
    file_name: str = Field(...)
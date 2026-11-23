from pydantic import BaseModel


class UserQuery(BaseModel):
    prompt: str
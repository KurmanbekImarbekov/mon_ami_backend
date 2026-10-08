from pydantic import BaseModel


class AIRequest(BaseModel):
    message: str
    exclude_ids: list[str] = []

from pydantic import BaseModel

class RequestModel(BaseModel):
    message: str
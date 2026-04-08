from pydantic import BaseModel, constr

class RequestModel(BaseModel):
    message: constr(strip_whitespace=True, min_length=1, max_length=2000)

from pydantic import BaseModel

class Apikey(BaseModel):
    key: str
    created_at: int
    id: str

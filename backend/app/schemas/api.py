from pydantic import BaseModel

class AskRequest(BaseModel):
    query: str
    owner_id: str
    
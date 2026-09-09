from pydantic import BaseModel

class Create_Todo(BaseModel):
    title: str
from pydantic import BaseModel
from typing import Optional

class Create_Todo(BaseModel):
    title: str

class Update_Todo(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
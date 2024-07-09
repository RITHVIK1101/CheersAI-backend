from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class Message(BaseModel):
    user_id: str
    message: str
    response: str

class Goal(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: datetime
    due_date: datetime
    created_by: str
    progress: Optional[int] = Field(0, ge=0, le=100)
    status: Optional[str] = "not started"

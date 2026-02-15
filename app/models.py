from sqlmodel import SQLModel, Field
from uuid import uuid4
from typing import Optional
from datetime import datetime

class Job(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    status: str = "created"

    input_path: Optional[str] = None
    transcript_path: Optional[str] = None

    error_message: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
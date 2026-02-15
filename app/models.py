from sqlmodel import SQLModel, Field
from uuid import uuid4
from typing import Optional


class Job(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    status: str = "created"
    input_path: Optional[str] = None
    transcript_path: Optional[str] = None
from datetime import datetime

from typing import Optional
from pydantic import BaseModel, Field


class FilePath(BaseModel):
    # id: Optional[str]
    path: str = Field(...)
    state: str = Field(...)
    created_by: int
    updated_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True # type: ignore
    }

class UpdateFilePath(BaseModel):
    # id: Optional[str]
    path: Optional[str] = None
    state: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {
        "from_attributes": True # type: ignore
    }

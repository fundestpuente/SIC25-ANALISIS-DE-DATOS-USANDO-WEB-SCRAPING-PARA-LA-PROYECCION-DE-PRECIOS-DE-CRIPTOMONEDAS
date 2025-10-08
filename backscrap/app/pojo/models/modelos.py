from pydantic import BaseModel, Field
from typing import Generic, TypeVar, List, Optional
from datetime import datetime, timezone

T = TypeVar('T')

class CustomResponse(BaseModel, Generic[T]):
    status: int
    message: str
    data: T

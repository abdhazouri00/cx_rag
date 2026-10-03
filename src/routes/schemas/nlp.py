from pydantic import BaseModel
from typing import Optional

class PushRequest(BaseModel):
  do_reset: Optional[int] = 0
  pagesize: Optional[int] = 100

class SearchRequest(BaseModel):
  text: str
  limit: Optional[int] = 5
  conversation_id: Optional[str] = None

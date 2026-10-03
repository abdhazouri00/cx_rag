from .cx_rag_base import SQLBASE
from sqlalchemy import Column, Integer, UnicodeText, DateTime, ForeignKey, func, Index, Uuid, JSON
from sqlalchemy.orm import relationship
from pydantic import BaseModel
import uuid

class DataChunk(SQLBASE):
  __tablename__ = "chunks"

  chunk_id = Column(Integer, primary_key=True, index=True)
  chunk_uuid = Column(Uuid(as_uuid=True), unique=True, index=True,nullable=False, default=uuid.uuid4)

  chunk_text = Column(UnicodeText, nullable=False)
  chunk_metadata = Column(JSON, nullable=True)
  chunk_order = Column(Integer, nullable=False)

  created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
  updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True) 

  chunk_asset_id = Column(Integer, ForeignKey("assets.asset_id"), nullable=False)

  asset = relationship("Asset", back_populates="chunks")

  __table_args__ = (
    Index('ix_chunk_asset_id', chunk_asset_id),
  )

class RetrievedDocument(BaseModel):
  text: str
  score: float
  metadata: dict = {}
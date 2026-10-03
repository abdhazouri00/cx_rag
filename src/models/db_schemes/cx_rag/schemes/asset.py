from .cx_rag_base import SQLBASE
from sqlalchemy import Column, Integer, Unicode, DateTime, ForeignKey, func, Index, Uuid, JSON
from sqlalchemy.orm import relationship
import uuid

class Asset(SQLBASE):

  __tablename__ = "assets"

  asset_id = Column(Integer, primary_key=True, index=True)
  asset_uuid = Column(Uuid(as_uuid=True), unique=True, index=True,nullable=False, default=uuid.uuid4)

  asset_type = Column(Unicode(50), nullable=False)
  asset_name = Column(Unicode(255), nullable=False)
  asset_size = Column(Integer, nullable=False)
  asset_config = Column(JSON, nullable=True)

  created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
  updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True) 

  chunks = relationship("DataChunk", back_populates="asset")

  __table_args__ = (
    Index('ix_asset_type', asset_type),
  )
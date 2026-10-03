from .cx_rag_base import SQLBASE
from sqlalchemy import Column, Integer, Unicode, UnicodeText, DateTime, func, Index

class Message(SQLBASE):
  __tablename__ = "messages"

  message_id = Column(Integer, primary_key=True, index=True)

  message_conversation_id = Column(Unicode(64), nullable=False)
  message_role = Column(Unicode(20), nullable=False)
  message_content = Column(UnicodeText, nullable=False)

  created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

  __table_args__ = (
    Index('ix_message_conversation_id', message_conversation_id),
  )

from app.db import Base
from sqlalchemy import Column, BigInteger, String, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship

class Message(Base):
    __tablename__ = 'messages'
    id = Column(BigInteger, primary_key=True)
    customer_id = Column(BigInteger, ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)
    message_type = Column(String(10), nullable=False)
    evaluated_at = Column(DateTime(timezone=True), nullable=False)
    customer = relationship("Customer", back_populates="messages")
    __table_args__ = (
        Index('idx_messages_customer_eval', 'customer_id', 'evaluated_at'),
    )
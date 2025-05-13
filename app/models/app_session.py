from app.db import Base
from sqlalchemy import Column, BigInteger, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship

class AppSession(Base):
    __tablename__ = 'app_sessions'
    id = Column(BigInteger, primary_key=True)
    customer_id = Column(BigInteger, ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)
    session_timestamp = Column(DateTime(timezone=True), nullable=False)
    customer = relationship("Customer", back_populates="sessions")
    __table_args__ = (
        Index('idx_sessions_customer_ts', 'customer_id', 'session_timestamp'),
    )
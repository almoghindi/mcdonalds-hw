from app.db import Base
from sqlalchemy import Column, BigInteger, Numeric, DateTime, Index, ForeignKey
from sqlalchemy.orm import relationship

class Purchase(Base):
    __tablename__ = 'purchases'
    id = Column(BigInteger, primary_key=True)
    customer_id = Column(BigInteger, ForeignKey('customers.customer_id', ondelete='CASCADE'), nullable=False)
    purchase_timestamp = Column(DateTime(timezone=True), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    customer = relationship("Customer", back_populates="purchases")
    __table_args__ = (
        Index('idx_purchases_customer_ts', 'customer_id', 'purchase_timestamp'),
    )
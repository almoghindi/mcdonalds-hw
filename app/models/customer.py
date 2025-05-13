from app.db import Base
from sqlalchemy import Column, BigInteger
from sqlalchemy.orm import relationship

class Customer(Base):
    __tablename__ = 'customers'
    customer_id = Column(BigInteger, primary_key=True)
    sessions = relationship("AppSession", back_populates="customer")
    purchases = relationship("Purchase", back_populates="customer")
    messages = relationship("Message", back_populates="customer")
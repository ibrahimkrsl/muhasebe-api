from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# SQLAlchemy için Base Model Tanımlaması
Base = declarative_base()

# Kullanıcı Modeli
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="user")

    # Kullanıcının faturaları ve işlemleri ile ilişkisi
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete")
    invoices = relationship("Invoice", back_populates="user", cascade="all, delete")
    accounts = relationship("Account", back_populates="user", cascade="all, delete")

# Cari Takip Modeli (Müşteri Hesapları)
class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    last_transaction = Column(DateTime, default=datetime.utcnow)
    credit_limit = Column(Float, default=0.0)  # Kredi limiti
    user_id = Column(Integer, ForeignKey("users.id"))  # Kullanıcı ID'si

    user = relationship("User", back_populates="accounts")  # Kullanıcı ile ilişki
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete")
   

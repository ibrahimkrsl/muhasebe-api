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

    transactions = relationship("Transaction", back_populates="user", cascade="all, delete")
    invoices = relationship("Invoice", back_populates="user", cascade="all, delete")
    accounts = relationship("Account", back_populates="user", cascade="all, delete")

# Cari Hesap Modeli (Müşteri Hesapları)
class Account(Base):
    __tablename__ = "accounts"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    balance = Column(Float, default=0.0)
    last_transaction = Column(DateTime, default=datetime.utcnow)
    credit_limit = Column(Float, default=0.0)  # Kredi limiti
    user_id = Column(Integer, ForeignKey("users.id"))  # Kullanıcı ID'si

    user = relationship("User", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account", cascade="all, delete")
    invoices = relationship("Invoice", back_populates="account", cascade="all, delete")
    payment_plans = relationship("PaymentPlan", back_populates="account", cascade="all, delete")

# Gelir/Gider Modeli (Düzeltilmiş)
class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # "income" veya "expense"
    description = Column(String)
    date = Column(DateTime, default=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    user = relationship("User", back_populates="transactions")
    account = relationship("Account", back_populates="transactions")

# Fatura Modeli (Eklendi)
class Invoice(Base):
    __tablename__ = "invoices"
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, nullable=False)
    total_amount = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    paid = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id"))
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)

    user = relationship("User", back_populates="invoices")
    account = relationship("Account", back_populates="invoices")

# Ödeme Planı Modeli (Eklendi)
class PaymentPlan(Base):
    __tablename__ = "payment_plans"
    id = Column(Integer, primary_key=True, index=True)
    due_date = Column(DateTime, nullable=False)
    amount_due = Column(Float, nullable=False)
    paid = Column(Boolean, default=False)

    account_id = Column(Integer, ForeignKey("accounts.id"))
    account = relationship("Account", back_populates="payment_plans")

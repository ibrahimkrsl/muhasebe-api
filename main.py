from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import engine, get_db  # Veritabanı bağlantısı
import models  # Modelleri içe aktarıyoruz
from datetime import datetime

# FastAPI uygulaması
app = FastAPI()

# Veritabanı tablolarını oluştur
models.Base.metadata.create_all(bind=engine)

# Kullanıcı oluşturma endpoint'i
@app.post("/users/")
def create_user(username: str, password: str, role: str = "user", db: Session = Depends(get_db)):
    new_user = models.User(username=username, password=password, role=role)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# Cari Hesaba Otomatik İşlem Kaydı
@app.post("/transactions/auto")
def auto_transaction(account_id: int, amount: float, type: str, description: str, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Cari hesap bulunamadı")

    transaction = models.Transaction(amount=amount, type=type, description=description, account_id=account_id)
    db.add(transaction)

    if type == "income":
        account.balance += amount
    elif type == "expense":
        account.balance -= amount

    account.last_transaction = datetime.utcnow()
    db.commit()
    db.refresh(account)
    db.refresh(transaction)
    return {"message": "Cari hesap otomatik güncellendi", "account_balance": account.balance}

# Cari Hesaba Otomatik Fatura Kaydı
@app.post("/invoices/auto")
def auto_invoice(account_id: int, customer_name: str, total_amount: float, paid: bool = False, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Cari hesap bulunamadı")

    invoice = models.Invoice(customer_name=customer_name, total_amount=total_amount, paid=paid, account_id=account_id)
    db.add(invoice)

    if not paid:
        account.balance -= total_amount  # Fatura borç olarak eklenir
        payment_plan = models.PaymentPlan(account_id=account_id, due_date=datetime.utcnow(), amount_due=total_amount, paid=False)
        db.add(payment_plan)
    else:
        account.balance += total_amount  # Fatura ödendiği için gelir eklenir

    account.last_transaction = datetime.utcnow()
    db.commit()
    db.refresh(account)
    db.refresh(invoice)
    return {"message": "Cari hesap fatura işlemi tamamlandı", "account_balance": account.balance}

# Otomatik Vade Takibi
@app.get("/payment-plans/")
def get_payment_plans(db: Session = Depends(get_db)):
    return db.query(models.PaymentPlan).all()

@app.post("/payment-plans/pay")
def pay_due(account_id: int, amount: float, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Cari hesap bulunamadı")

    due_payments = db.query(models.PaymentPlan).filter(models.PaymentPlan.account_id == account_id, models.PaymentPlan.paid == False).order_by(models.PaymentPlan.due_date).all()
    if not due_payments:
        raise HTTPException(status_code=400, detail="Ödenmemiş vade bulunamadı")

    remaining_amount = amount
    for payment in due_payments:
        if remaining_amount >= payment.amount_due:
            remaining_amount -= payment.amount_due
            payment.paid = True
        else:
            payment.amount_due -= remaining_amount
            remaining_amount = 0
        if remaining_amount == 0:
            break

    account.balance += amount  # Ödeme yapıldığı için bakiye artar
    db.commit()
    db.refresh(account)
    return {"message": "Vade ödemesi gerçekleştirildi", "account_balance": account.balance}

# Yeni Ödeme Planı Oluşturma Endpoint'i
@app.post("/payment-plans/")
def create_payment_plan(account_id: int, due_date: str, amount_due: float, paid: bool = False, db: Session = Depends(get_db)):
    account = db.query(models.Account).filter(models.Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Cari hesap bulunamadı")

    new_payment_plan = models.PaymentPlan(account_id=account_id, due_date=due_date, amount_due=amount_due, paid=paid)
    db.add(new_payment_plan)
    db.commit()
    db.refresh(new_payment_plan)
    return new_payment_plan


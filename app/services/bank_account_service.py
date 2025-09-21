# app/services/bank_account_service.py
from app.database import SessionLocal
from app.models.bank_account import BankAccount

class BankAccountService:
    def __init__(self):
        self.db = SessionLocal()

    def get_all_bank_accounts(self):
        return self.db.query(BankAccount).all()

    def get_bank_account_by_id(self, bank_account_id: int):
        return self.db.query(BankAccount).filter(BankAccount.id == bank_account_id).first()

    def create_bank_account(self, data):
        bank_account = BankAccount(**data)
        self.db.add(bank_account)
        self.db.commit()
        self.db.refresh(bank_account)
        return bank_account
# app/services/check_service.py
from app.database import SessionLocal
from app.models.check import Check
from app.utils.state_machine import CheckStateMachine

class CheckService:
    def __init__(self):
        self.db = SessionLocal()

    def create_check(self, data):
        check = Check(**data)
        self.db.add(check)
        self.db.commit()
        self.db.refresh(check)
        return check

    def get_all_checks(self):
        return self.db.query(Check).order_by(Check.due_date.desc()).all()

    def change_check_status(self, check_id: int, new_status: str):
        check = self.db.query(Check).filter(Check.id == check_id).first()
        if not check:
            raise Exception("چک یافت نشد.")

        # ایجاد state machine
        sm = CheckStateMachine(check)
        
        # اعمال انتقال — مثال: sm.issue() یا sm.clear()
        transition_method = getattr(sm, new_status, None)
        if not transition_method:
            raise ValueError(f"انتقال '{new_status}' معتبر نیست.")
        
        transition_method()
        
        # ذخیره وضعیت جدید
        check.status = sm.state
        self.db.commit()
        self.db.refresh(check)
        return check
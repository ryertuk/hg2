# app/utils/state_machine.py
from transitions import Machine

class CheckStateMachine:
    states = ['registered', 'issued', 'in_hand', 'deposited', 'cleared', 'bounced', 'endorsed', 'reconciled', 'cancelled']

    def __init__(self, check):
        self.check = check
        self.machine = Machine(model=self, states=CheckStateMachine.states, initial=check.status)
        
        # تعاریف انتقال — مثال ساده
        self.machine.add_transition('issue', 'registered', 'issued')
        self.machine.add_transition('receive', 'issued', 'in_hand')
        self.machine.add_transition('deposit', 'in_hand', 'deposited')
        self.machine.add_transition('clear', 'deposited', 'cleared')
        self.machine.add_transition('bounce', 'deposited', 'bounced')
        self.machine.add_transition('cancel', '*', 'cancelled')

    def on_enter_state(self):
        """به‌روزرسانی وضعیت در دیتابیس — فراخوانی پس از هر انتقال"""
        self.check.status = self.state
        # در عمل: باید session.commit() شود — در سرویس انجام می‌شود
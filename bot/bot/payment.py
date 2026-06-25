"""In-memory payment/subscription state management."""
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class PaymentState:
    paid_mode: bool = False
    amount: float = 0.0
    currency: str = "INR"
    qr_file_id: str | None = None
    payment_description: str = "Pay to access premium content"
    upi_id: str = ""
    paid_users: set[int] = field(default_factory=set)
    pending: dict[int, dict] = field(default_factory=dict)

_state = PaymentState()

def is_paid_mode() -> bool:         return _state.paid_mode
def set_paid_mode(v: bool):          _state.paid_mode = v
def get_amount() -> float:           return _state.amount
def set_amount(v: float):            _state.amount = v
def get_currency() -> str:           return _state.currency
def get_qr_file_id() -> str | None:  return _state.qr_file_id
def set_qr_file_id(fid: str):        _state.qr_file_id = fid
def get_description() -> str:        return _state.payment_description
def set_description(v: str):         _state.payment_description = v
def get_upi() -> str:                return _state.upi_id
def set_upi(v: str):                 _state.upi_id = v

def is_user_paid(tid: int) -> bool:  return tid in _state.paid_users
def mark_paid(tid: int):             _state.paid_users.add(tid)
def revoke_user(tid: int):           _state.paid_users.discard(tid)

def add_pending(tid: int, info: dict):
    _state.pending[tid] = {**info, "at": datetime.now().strftime("%d %b %H:%M")}

def get_pending() -> dict:           return dict(_state.pending)
def approve_pending(tid: int):
    mark_paid(tid)
    _state.pending.pop(tid, None)

def reject_pending(tid: int):
    _state.pending.pop(tid, None)

def get_settings_text() -> str:
    status = "🟢 ON" if _state.paid_mode else "🔴 OFF"
    return (f"💳 <b>Payment Settings</b>\n\n"
            f"Status: <b>{status}</b>\n"
            f"Amount: <b>₹{_state.amount:.0f}</b>\n"
            f"UPI ID: <b>{_state.upi_id or 'Not set'}</b>\n"
            f"QR Code: {'✅ Set' if _state.qr_file_id else '❌ Not set'}\n"
            f"Paid Users: <b>{len(_state.paid_users)}</b>\n"
            f"Pending: <b>{len(_state.pending)}</b>")

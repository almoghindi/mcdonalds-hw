import pytest
from datetime import datetime
import app.services.messaging_service as msg_service
from app.models.message import Message

class DummyDB:
    def __init__(self):
        self.add_called = False
        self.commit_called = False
        self.rollback_called = False

    def add(self, obj):
        self.add_called = True
        obj.id = 123

    def commit(self):
        self.commit_called = True

    def rollback(self):
        self.rollback_called = True

@pytest.fixture(autouse=True)
def fixed_datetime(monkeypatch):
    fixed = datetime(2025, 1, 1, 12, 0, 0)
    class FrozenDateTime:
        @classmethod
        def now(cls):
            return fixed
    monkeypatch.setattr(msg_service, 'datetime', FrozenDateTime)
    return fixed

@pytest.mark.parametrize("msg_type", ["BOOST", "REWARD"])
def test_valid_message_types(msg_type, monkeypatch, fixed_datetime):
    dummy_db = DummyDB()
    monkeypatch.setattr(msg_service, 'get_db', lambda: dummy_db)

    result = msg_service.message_customer(customer_id=42, message_type=msg_type)

    assert isinstance(result, Message)
    assert result.customer_id == 42
    assert result.message_type == msg_type
    assert result.evaluated_at == fixed_datetime

    assert dummy_db.add_called, "Expected add() to be called"
    assert dummy_db.commit_called, "Expected commit() to be called"
    assert not dummy_db.rollback_called, "Did not expect rollback()"

@pytest.mark.parametrize("bad_type", ["NONE", "", "INVALID"])
def test_invalid_message_types(bad_type, monkeypatch):
    dummy_db = DummyDB()
    monkeypatch.setattr(msg_service, 'get_db', lambda: dummy_db)

    result = msg_service.message_customer(customer_id=99, message_type=bad_type)
    assert result is None
    assert not dummy_db.add_called
    assert not dummy_db.commit_called
    assert not dummy_db.rollback_called

def test_exception_during_db(monkeypatch):
    class ErrorDB(DummyDB):
        def add(self, obj):
            super().add(obj)
            raise RuntimeError("DB failure")

    error_db = ErrorDB()
    monkeypatch.setattr(msg_service, 'get_db', lambda: error_db)

    with pytest.raises(RuntimeError):
        msg_service.message_customer(customer_id=7, message_type="BOOST")
    assert error_db.rollback_called

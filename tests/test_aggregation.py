import pytest
from datetime import timedelta, timezone
import app.services.aggregation_service as agg_service
from app.services.aggregation_service import aggregate_per_customer

class SessionObj:
    def __init__(self, customer_id, timestamp):
        self.customer_id = customer_id
        self.session_timestamp = timestamp

class PurchaseObj:
    def __init__(self, customer_id, amount, timestamp):
        self.customer_id = customer_id
        self.amount = amount
        self.purchase_timestamp = timestamp

@ pytest.fixture(autouse=True)
def fixed_now(monkeypatch):
    fixed = agg_service.datetime.now(timezone.utc)
    class FrozenDateTime:
        @classmethod
        def now(cls, tz=None):
            return fixed

    monkeypatch.setattr(agg_service, 'datetime', FrozenDateTime)
    yield


def test_no_data():
    result = aggregate_per_customer([], [])
    assert result == []


def test_only_purchases():
    now = agg_service.datetime.now(timezone.utc)
    in_window = now - timedelta(days=7)
    old = now - timedelta(days=100)

    purchases = [PurchaseObj(1, 10.0, in_window), PurchaseObj(1, 5.0, old)]
    result = aggregate_per_customer([], purchases, weeks=8)
    assert len(result) == 1
    r = result[0]

    assert r['customer_id'] == 1
    assert pytest.approx(r['total_spend']) == 10.0
    assert r['avg_weekly_sessions'] == 0.0


def test_only_sessions():
    now = agg_service.datetime.now(timezone.utc)
    ts1 = now - timedelta(days=1)
    ts2 = now - timedelta(days=10)
    sessions = [SessionObj(1, ts1), SessionObj(1, ts2), SessionObj(2, ts1)]

    result = aggregate_per_customer(sessions, [], weeks=8)
    assert len(result) == 2

    r1 = next(r for r in result if r['customer_id'] == 1)
    assert pytest.approx(r1['avg_weekly_sessions']) == 2/8
    assert r1['total_spend'] == 0.0

    r2 = next(r for r in result if r['customer_id'] == 2)
    assert pytest.approx(r2['avg_weekly_sessions']) == 1/8
    assert r2['total_spend'] == 0.0


def test_mixed_data():
    now = agg_service.datetime.now(timezone.utc)
    sess_ts = now - timedelta(days=3)
    purch_ts = now - timedelta(days=5)
    sessions = [SessionObj(1, sess_ts), SessionObj(1, sess_ts)]
    purchases = [PurchaseObj(1, 7.5, purch_ts)]

    result = aggregate_per_customer(sessions, purchases, weeks=8)
    assert len(result) == 1
    r = result[0]

    assert r['customer_id'] == 1
    assert pytest.approx(r['total_spend']) == 7.5
    assert pytest.approx(r['avg_weekly_sessions']) == 2/8


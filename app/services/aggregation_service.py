import os
from app.db import get_db
from app.logger import logger
from datetime import datetime, timedelta, timezone
from app.models import AppSession, Purchase, Customer
from .messaging_service import message_customer

from dotenv import load_dotenv
load_dotenv()

LOW_SPEND_THRESHOLD = float(os.getenv("LOW_SPEND_THRESHOLD"))
HIGH_ACTIVITY_THRESHOLD = float(os.getenv("HIGH_ACTIVITY_THRESHOLD"))
if not LOW_SPEND_THRESHOLD or not HIGH_ACTIVITY_THRESHOLD:
    raise RuntimeError("LOW_SPEND_THRESHOLD or HIGH_ACTIVITY_THRESHOLD not set in .env")

def read_sessions_and_purchases():
    db = get_db()
    sessions = db.query(AppSession).all()
    purchases = db.query(Purchase).all()
    logger.info(f"Read {len(sessions)} sessions and {len(purchases)} purchases")
    return sessions, purchases

def aggregate_per_customer(sessions, purchases, weeks:int =8):
    eight_weeks_time = datetime.now(timezone.utc) - timedelta(weeks=weeks)
    customers_spend_dict = {}
    customers_session_dict = {}

    for p in purchases:
        purchase_time = p.purchase_timestamp
        if purchase_time.tzinfo is None:
            purchase_time = purchase_time.replace(tzinfo=timezone.utc)
        if purchase_time >= eight_weeks_time:
            cid = p.customer_id
            amount = float(p.amount)
            customers_spend_dict[cid] = customers_spend_dict.get(cid, 0.0) + amount
    logger.info("Aggregated {} purchases".format(len(purchases)))

    for s in sessions:
        session_time = s.session_timestamp
        if session_time.tzinfo is None:
            session_time = session_time.replace(tzinfo=timezone.utc)
        if session_time >= eight_weeks_time:
            cid = s.customer_id
            customers_session_dict[cid] = customers_session_dict.get(cid, 0) + 1
    logger.info("Aggregated {} sessions".format(len(sessions)))

    results = []
    customer_ids = set(customers_spend_dict.keys()) | set(customers_session_dict.keys())
    for cid in sorted(customer_ids):
        total_spend = customers_spend_dict.get(cid, 0.0)
        total_sessions = customers_session_dict.get(cid, 0)
        avg_weekly = total_sessions / weeks
        results.append({
            'customer_id': cid,
            'total_spend': total_spend,
            'avg_weekly_sessions': avg_weekly
        })

    logger.info(f"Aggregated {len(results)} customers.")

    return results

def decide_message_type(aggregated_results):
    for r in aggregated_results:
        if r['total_spend'] < LOW_SPEND_THRESHOLD:
            message_type = 'BOOST'
        elif r['avg_weekly_sessions'] > HIGH_ACTIVITY_THRESHOLD:
            message_type = 'REWARD'
        else:
            message_type = 'NONE'
        
        logger.info(f"Customer {r['customer_id']} is {message_type}")
        yield r['customer_id'], message_type

def aggregation_and_messaging():
    sessions, purchases = read_sessions_and_purchases()
    results = aggregate_per_customer(sessions, purchases)

    logger.info(f"Aggregated {len(results)} customers.")

    for customer_id, message_type in decide_message_type(results):
        message_customer(customer_id, message_type)
    
    logger.info("Aggregation and messaging complete.")
from datetime import datetime, timedelta
import numpy as np
from sqlalchemy import delete
from .db import get_db
from .logger import logger

from app.models import Customer, AppSession, Purchase

def generate_and_insert(
    n_customers: int = 10_000,
    weeks: int = 8,
    sess_lambda: float = 5.0, # Poisson distribution λ for average sessions per customer per week.
    purch_lambda: float = 1.0, # Poisson distribution λ for average purchases per customer per week.
    lognorm_mean: float = 3.0, # Mean (μ) parameter for log-normal distribution of purchase amounts.
    lognorm_sigma: float = 1.0, # Standard deviation (σ) parameter for log-normal distribution of purchase amounts.
):
    db = get_db()
    try:
        db.execute(delete(AppSession))
        db.execute(delete(Purchase))
        db.execute(delete(Customer))
        db.commit()

        customers = [Customer(customer_id=i) for i in range(1, n_customers + 1)]
        db.bulk_save_objects(customers)
        db.commit()

        session_objs = []
        purchase_objs = []
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=weeks)

        for cust_id in range(1, n_customers + 1):
            weekly_sessions = np.random.poisson(sess_lambda, size=weeks)
            for wk, count in enumerate(weekly_sessions):
                week_start = start_date + timedelta(weeks=wk)
                for _ in range(count):
                    ts = week_start + timedelta(seconds=np.random.rand() * 7 * 24 * 3600)
                    session_objs.append(AppSession(customer_id=cust_id, session_timestamp=ts))

            weekly_purchases = np.random.poisson(purch_lambda, size=weeks)
            for wk, count in enumerate(weekly_purchases):
                week_start = start_date + timedelta(weeks=wk)
                for _ in range(count):
                    ts = week_start + timedelta(seconds=np.random.rand() * 7 * 24 * 3600)
                    amt = float(np.random.lognormal(lognorm_mean, lognorm_sigma))
                    purchase_objs.append(Purchase(customer_id=cust_id, purchase_timestamp=ts, amount=amt))

        db.bulk_save_objects(session_objs)
        db.bulk_save_objects(purchase_objs)
        db.commit()

        logger.info(f"Inserted {n_customers} customers.")
        logger.info(f"Inserted {len(session_objs)} session records.")
        logger.info(f"Inserted {len(purchase_objs)} purchase records.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

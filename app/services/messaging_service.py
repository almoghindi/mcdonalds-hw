from app.models.message import Message
from app.db import get_db
from app.logger import logger
from datetime import datetime

def message_customer(customer_id: int, message_type: str):
    valid_types = {"BOOST", "REWARD"}
    if message_type not in valid_types:
        logger.info("Customer type message is NONE, no SMS sent")
        return None

    logger.info(f"Customer {message_type} SMS sent successfully for customer {customer_id}")

    db = get_db()

    try:
        msg = Message(
            customer_id=customer_id,
            message_type=message_type,
            evaluated_at=datetime.now()
        )
        db.add(msg)
        db.commit()
        return msg
    except Exception:
        db.rollback()
        logger.error(f"Failed to record message for customer {customer_id}")
        raise
import schedule, threading
from app.services.aggregation_service import aggregation_and_messaging

schedule.every(8).weeks.do(aggregation_and_messaging)

def start_aggregation_and_messaging_scheduler():
    def runner():
        while True:
            schedule.run_pending()
    thread = threading.Thread(target=runner, daemon=True)
    thread.start()

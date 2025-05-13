import app.models
from contextlib import asynccontextmanager
from .logger import logger
from .generate_data import generate_and_insert
from app.services.aggregation_service import aggregation_and_messaging
from .scheduler import start_aggregation_and_messaging_scheduler
from .db import init_db, migrate

from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting application initialization…")
    init_db()
    logger.info("Initialization complete.")

    yield

app = FastAPI(lifespan=lifespan)

@app.get("/seed", tags=["Seeding"], summary="Generate and insert synthetic data")
def seed():
    generate_and_insert()
    return {"status": "success"}


@app.get("/aggregate-and-message-test", tags=["Aggregation"], summary="Run aggregation and messaging logic")
def aggregate_and_message_test():
    aggregation_and_messaging()
    return {"status": "success"}

@app.get("/migrate", tags=["Migrations"], summary="Run DB migrations")
def migrate_db():
    migrate()
    return {"status": "success"}

start_aggregation_and_messaging_scheduler()
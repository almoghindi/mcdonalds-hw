import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
import psycopg2
from .logger import logger

from alembic import command
from alembic.config import Config

from dotenv import load_dotenv
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL not set in .env")


engine = create_engine(DATABASE_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db():
    logger.info("Ensuring database tables exist…")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables are ready.")
    except psycopg2.OperationalError:
        logger.error("Database tables already exist.")

def get_db():
    try:
        logger.info("Database connection established.")
        return SessionLocal()
    except psycopg2.OperationalError:
        logger.error("Database connection already established.")


def migrate():
    cfg = Config("alembic.ini")
    command.upgrade(cfg, "head")
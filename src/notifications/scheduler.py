from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED

from src.logger import logger
from src.notifications.constants import UPDATING_TASK_ID
from src.notifications.database import Database


def event_listener(event):
    if event.exception:
        logger.error(event.exception)
    else:
        if event.job_id != UPDATING_TASK_ID:
            Database.insert_notification(game_id=event.job_id, completed_at=datetime.now())


job_stores = {"default": SQLAlchemyJobStore(url="sqlite:///notifications_db.sqlite")}
job_defaults = {"coalesce": False, "max_instances": 1}
scheduler = AsyncIOScheduler(jobstores=job_stores, job_defaults=job_defaults)
scheduler.add_listener(event_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

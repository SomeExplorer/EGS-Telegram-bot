from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


def event_listener(event):
    print(f"Event received: {event}")
    if event.exception:
        print(event.exception)


job_stores = {"default": SQLAlchemyJobStore(url="sqlite:///jobs.sqlite")}
job_defaults = {"coalesce": False, "max_instances": 1}
scheduler = BackgroundScheduler(jobstores=job_stores, job_defaults=job_defaults)
scheduler.add_listener(event_listener)

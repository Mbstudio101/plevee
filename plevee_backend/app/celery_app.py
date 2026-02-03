"""
Celery configuration for Plevee backend
"""
from celery import Celery
from app.config import settings

# Create Celery app
celery_app = Celery(
    "plevee",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.strategy_executor"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Task routes
celery_app.conf.task_routes = {
    "app.tasks.strategy_executor.*": {"queue": "strategies"},
    "app.tasks.market_data.*": {"queue": "market_data"},
}

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "update-market-data": {
        "task": "app.tasks.market_data.update_prices",
        "schedule": 60.0,  # Every 60 seconds
    },
}

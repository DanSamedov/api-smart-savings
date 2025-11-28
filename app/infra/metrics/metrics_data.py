# app/infra/metrics/metrics_data.py
from datetime import datetime, timezone

import psutil
from pydantic import BaseModel
from sqlmodel import select


class Metrics:
    def __init__(self):
        self.startup_time: datetime = datetime.now()
        self.uptime: str = ''
        self.system_metrics: dict = {}
        self.db_status: bool = False
        self.latest_response_latency: float = 0.0

    def set_latest_response_latency(self, latency: float):
        self.latest_response_latency = latency


class Metrics_V2(BaseModel):
    startup_time: datetime = datetime.now(timezone.utc)
    uptime: str = ''
    system_metrics: dict = {}
    db_active: bool = False
    latest_response_latency: float = 0.0

    def set_latest_response_latency(self, latency: float) -> None:
        self.latest_response_latency = latency


def get_uptime(start_time: datetime) -> str:
    """
    Calculate uptime from start_time to now.
    """
    now = datetime.now(timezone.utc)
    delta = now - start_time
    days, seconds = divmod(delta.total_seconds(), 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    return f"{days}d {int(hours)}h {int(minutes)}m {int(seconds)}s"


def get_system_metrics() -> dict:
    """
    Gather basic system metrics like CPU and memory usage.
    """
    cpu_usage = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory()
    memory_usage = memory.percent

    return {
        "cpu_usage_percent": cpu_usage,
        "memory_usage_percent": memory_usage,
    }


async def get_db_status() -> bool:
    """
    Check database connectivity status.
    """
    # Import here to avoid initializing the database at module import time
    from app.infra.database.session import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        try:
            session.execute(select(1))
            return True
        except Exception:
            return False
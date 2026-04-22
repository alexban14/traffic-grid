"""
Worker heartbeat — registers this Celery worker with the control plane DB.

Uses Celery worker signals to send heartbeats on startup and periodically.
Each worker sends its hostname, type, and IP to the workers table.
"""

import os
import socket
import logging
from datetime import datetime
from celery.signals import worker_ready, heartbeat_sent
from sqlmodel import Session, select
from app.db.session import engine
from app.models.worker import Worker

logger = logging.getLogger(__name__)


def _get_worker_ip() -> str:
    """Get the worker's IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("10.20.20.200", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "unknown"


def _get_worker_name() -> str:
    """Get the worker name from env or hostname."""
    return os.environ.get("WORKER_NAME", socket.gethostname())


def _get_worker_type() -> str:
    """Determine worker type from environment."""
    return os.environ.get("WORKER_TYPE", "LXC-Selenium")


def _send_heartbeat():
    """Register/update this worker in the database."""
    name = _get_worker_name()
    worker_type = _get_worker_type()
    ip = _get_worker_ip()

    try:
        with Session(engine) as session:
            statement = select(Worker).where(Worker.name == name)
            worker = session.exec(statement).first()

            if not worker:
                worker = Worker(name=name, type=worker_type, ip_address=ip)
                logger.info(f"Registering new worker: {name} ({worker_type}) at {ip}")
            else:
                worker.ip_address = ip

            worker.last_heartbeat = datetime.utcnow()
            worker.status = "IDLE"
            session.add(worker)
            session.commit()
    except Exception as e:
        logger.warning(f"Heartbeat failed: {e}")


@worker_ready.connect
def on_worker_ready(**kwargs):
    """Send initial heartbeat when worker starts."""
    _send_heartbeat()
    logger.info("Worker registered via heartbeat")


@heartbeat_sent.connect
def on_heartbeat_sent(**kwargs):
    """Send heartbeat periodically (Celery sends this every ~2 min by default)."""
    _send_heartbeat()

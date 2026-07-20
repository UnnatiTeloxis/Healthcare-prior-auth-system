"""Background job tracking for slow IG install operations."""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

logger = logging.getLogger(__name__)


class IgLoadJobState(str, Enum):
    pending = "pending"
    downloading = "downloading"
    installing = "installing"
    completed = "completed"
    failed = "failed"


@dataclass
class IgLoadJob:
    job_id: str
    package_id: str
    version: str | None = None
    status: IgLoadJobState = IgLoadJobState.pending
    message: str = ""
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    completed_at: str | None = None
    result: dict[str, Any] | None = None
    error: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "package_id": self.package_id,
            "version": self.version,
            "status": self.status.value,
            "message": self.message,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "result": self.result,
            "error": self.error,
        }


class IgLoadJobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, IgLoadJob] = {}
        self._active_by_package: dict[str, str] = {}
        self._lock = asyncio.Lock()

    def get(self, job_id: str) -> IgLoadJob | None:
        return self._jobs.get(job_id)

    def list_jobs(self, *, include_completed: bool = True) -> list[IgLoadJob]:
        jobs = list(self._jobs.values())
        if include_completed:
            return jobs
        return [
            job
            for job in jobs
            if job.status in {IgLoadJobState.pending, IgLoadJobState.downloading, IgLoadJobState.installing}
        ]

    def active_job_for_package(self, package_id: str) -> IgLoadJob | None:
        job_id = self._active_by_package.get(package_id)
        if not job_id:
            return None
        job = self._jobs.get(job_id)
        if job and job.status in {
            IgLoadJobState.pending,
            IgLoadJobState.downloading,
            IgLoadJobState.installing,
        }:
            return job
        return None

    async def start_job(
        self,
        package_id: str,
        version: str | None,
        worker,
    ) -> IgLoadJob:
        async with self._lock:
            existing = self.active_job_for_package(package_id)
            if existing:
                return existing

            job = IgLoadJob(
                job_id=str(uuid.uuid4()),
                package_id=package_id,
                version=version,
            )
            self._jobs[job.job_id] = job
            self._active_by_package[package_id] = job.job_id

        asyncio.create_task(self._run_job(job, worker))
        return job

    async def _run_job(self, job: IgLoadJob, worker) -> None:
        try:
            result = await worker(job)
            job.status = IgLoadJobState.completed
            job.message = "IG loaded successfully"
            job.result = result
            job.completed_at = datetime.now(timezone.utc).isoformat()
        except Exception as exc:
            logger.exception("IG load job %s failed", job.job_id)
            job.status = IgLoadJobState.failed
            job.message = "IG load failed"
            job.error = str(exc)
            job.completed_at = datetime.now(timezone.utc).isoformat()
        finally:
            self._active_by_package.pop(job.package_id, None)


ig_load_job_manager = IgLoadJobManager()

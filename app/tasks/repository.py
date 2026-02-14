from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from app.models.schemas import ListingTask, TaskStatus


class TaskRepository:
    def __init__(self, db_path: str = "data/autopilot.db") -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS listing_tasks (
                    task_id TEXT PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    listing_pack_version TEXT NOT NULL,
                    input_snapshot TEXT NOT NULL,
                    channel TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    output TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS task_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    payload TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS listing_task_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT NOT NULL,
                    step_name TEXT NOT NULL,
                    status TEXT NOT NULL,
                    retry_count INTEGER NOT NULL DEFAULT 0,
                    artifact_path TEXT,
                    error TEXT,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def save_task(self, task: ListingTask) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO listing_tasks
                (task_id, product_id, status, listing_pack_version, input_snapshot, channel, created_at, updated_at, output)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.task_id,
                    task.product_id,
                    task.status.value,
                    task.listing_pack_version,
                    json.dumps(task.input_snapshot, ensure_ascii=False),
                    task.channel,
                    task.created_at,
                    task.updated_at,
                    json.dumps(task.output, ensure_ascii=False),
                ),
            )

    def save_step(
        self,
        task_id: str,
        step_name: str,
        status: str,
        updated_at: str,
        retry_count: int = 0,
        artifact_path: str | None = None,
        error: str | None = None,
    ) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO listing_task_steps
                (task_id, step_name, status, retry_count, artifact_path, error, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (task_id, step_name, status, retry_count, artifact_path, error, updated_at),
            )

    def list_steps(self, task_id: str) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT step_name, status, retry_count, artifact_path, error, updated_at
                FROM listing_task_steps
                WHERE task_id = ?
                ORDER BY id ASC
                """,
                (task_id,),
            ).fetchall()
        return [
            {
                "step_name": row[0],
                "status": row[1],
                "retry_count": row[2],
                "artifact_path": row[3],
                "error": row[4],
                "updated_at": row[5],
            }
            for row in rows
        ]

    def log_step(self, task_id: str, step_name: str, success: bool, message: str, payload: dict, created_at: str) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO task_logs (task_id, step_name, success, message, payload, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (task_id, step_name, int(success), message, json.dumps(payload, ensure_ascii=False), created_at),
            )

    def get_task(self, task_id: str) -> ListingTask | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT task_id, product_id, status, listing_pack_version, input_snapshot, channel,
                       created_at, updated_at, output
                FROM listing_tasks WHERE task_id = ?
                """,
                (task_id,),
            ).fetchone()
        if row is None:
            return None
        return ListingTask(
            task_id=row[0],
            product_id=row[1],
            status=TaskStatus(row[2]),
            listing_pack_version=row[3],
            input_snapshot=json.loads(row[4]),
            channel=row[5],
            created_at=row[6],
            updated_at=row[7],
            output=json.loads(row[8]),
        )

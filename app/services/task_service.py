import sqlite3
from pathlib import Path
from typing import Any

from app.core.config import settings


class TaskService:
    def __init__(self) -> None:
        self.db_path: Path = settings.memory_db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'open',
                    priority TEXT NOT NULL DEFAULT 'normal',
                    notes TEXT,
                    session_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def create_task(
        self,
        title: str,
        session_id: str | None = None,
        priority: str = "normal",
        notes: str | None = None,
    ) -> dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO tasks (title, status, priority, notes, session_id)
                VALUES (?, 'open', ?, ?, ?)
                """,
                (title, priority, notes, session_id),
            )
            conn.commit()
            task_id = cur.lastrowid
        return self.get_task(task_id)

    def list_tasks(self, status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        query = "SELECT id, title, status, priority, notes, session_id, created_at, updated_at FROM tasks"
        params: list[Any] = []
        if status:
            query += " WHERE status = ?"
            params.append(status)
        query += " ORDER BY CASE status WHEN 'open' THEN 0 WHEN 'in_progress' THEN 1 ELSE 2 END, id DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_task(self, task_id: int) -> dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute(
                "SELECT id, title, status, priority, notes, session_id, created_at, updated_at FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()
        if not row:
            return {"ok": False, "error": f"Task not found: {task_id}"}
        task = self._row_to_dict(row)
        task["ok"] = True
        return task

    def update_status(self, task_id: int, status: str) -> dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (status, task_id),
            )
            conn.commit()
        return self.get_task(task_id)

    def _row_to_dict(self, row: tuple[Any, ...]) -> dict[str, Any]:
        return {
            "id": row[0],
            "title": row[1],
            "status": row[2],
            "priority": row[3],
            "notes": row[4],
            "session_id": row[5],
            "created_at": row[6],
            "updated_at": row[7],
        }


task_service = TaskService()

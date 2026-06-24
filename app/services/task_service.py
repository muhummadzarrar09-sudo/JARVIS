from pathlib import Path
from typing import Any

from app.core.config import settings
from app.services.sqlite_service import connect_sqlite


class TaskService:
    def __init__(self) -> None:
        self.db_path: Path = settings.memory_db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.allowed_statuses = {"open", "in_progress", "done"}
        self.allowed_priorities = {"low", "normal", "high"}

    def initialize(self) -> None:
        with connect_sqlite(self.db_path) as conn:
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
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status_id ON tasks(status, id DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_session_status ON tasks(session_id, status)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at DESC)")
            conn.commit()

    def create_task(
        self,
        title: str,
        session_id: str | None = None,
        priority: str = "normal",
        notes: str | None = None,
    ) -> dict[str, Any]:
        clean_title = (title or "").strip()
        clean_priority = (priority or "normal").strip().lower()
        if not clean_title:
            return {"ok": False, "error": "Task title is required."}
        if clean_priority not in self.allowed_priorities:
            return {"ok": False, "error": f"Invalid priority: {priority}"}

        with connect_sqlite(self.db_path) as conn:
            cur = conn.execute(
                """
                INSERT INTO tasks (title, status, priority, notes, session_id)
                VALUES (?, 'open', ?, ?, ?)
                """,
                (clean_title[:240], clean_priority, (notes or "")[:2000] or None, session_id),
            )
            conn.commit()
            task_id = cur.lastrowid
        return self.get_task(task_id)

    def list_tasks(self, status: str | None = None, limit: int = 100) -> list[dict[str, Any]]:
        query = "SELECT id, title, status, priority, notes, session_id, created_at, updated_at FROM tasks"
        params: list[Any] = []
        clean_status = (status or "").strip().lower() or None
        if clean_status:
            query += " WHERE status = ?"
            params.append(clean_status)
        query += " ORDER BY CASE status WHEN 'open' THEN 0 WHEN 'in_progress' THEN 1 ELSE 2 END, id DESC LIMIT ?"
        params.append(limit)

        with connect_sqlite(self.db_path) as conn:
            rows = conn.execute(query, tuple(params)).fetchall()
        return [self._row_to_dict(row) for row in rows]

    def get_task(self, task_id: int) -> dict[str, Any]:
        with connect_sqlite(self.db_path) as conn:
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
        clean_status = (status or "").strip().lower()
        if clean_status not in self.allowed_statuses:
            return {"ok": False, "error": f"Invalid task status: {status}", "allowed_statuses": sorted(self.allowed_statuses)}
        with connect_sqlite(self.db_path) as conn:
            cur = conn.execute(
                "UPDATE tasks SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (clean_status, task_id),
            )
            conn.commit()
            if cur.rowcount == 0:
                return {"ok": False, "error": f"Task not found: {task_id}"}
        return self.get_task(task_id)

    def current_task(self) -> dict[str, Any]:
        with connect_sqlite(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT id, title, status, priority, notes, session_id, created_at, updated_at
                FROM tasks
                WHERE status = 'in_progress'
                ORDER BY id ASC
                LIMIT 1
                """
            ).fetchone()
        if not row:
            return {"ok": False, "error": "No task is currently in progress."}
        task = self._row_to_dict(row)
        task["ok"] = True
        return task

    def next_task(self) -> dict[str, Any]:
        current = self.current_task()
        if current.get("ok"):
            return current
        with connect_sqlite(self.db_path) as conn:
            row = conn.execute(
                """
                SELECT id, title, status, priority, notes, session_id, created_at, updated_at
                FROM tasks
                WHERE status = 'open'
                ORDER BY id ASC
                LIMIT 1
                """
            ).fetchone()
        if not row:
            return {"ok": False, "error": "No open or in-progress tasks found."}
        task = self._row_to_dict(row)
        task["ok"] = True
        return task

    def task_summary(self) -> dict[str, Any]:
        with connect_sqlite(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT status, COUNT(*)
                FROM tasks
                GROUP BY status
                """
            ).fetchall()
        counts = {row[0]: row[1] for row in rows}
        return {
            "ok": True,
            "counts": counts,
            "open": counts.get("open", 0),
            "in_progress": counts.get("in_progress", 0),
            "done": counts.get("done", 0),
        }

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

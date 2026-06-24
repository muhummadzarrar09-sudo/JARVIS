from pathlib import Path
from typing import Any
from uuid import uuid4

from app.core.config import settings
from app.services.sqlite_service import connect_sqlite


class MemoryService:
    def __init__(self) -> None:
        self.db_path: Path = settings.memory_db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        with connect_sqlite(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_updated_at ON sessions(updated_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_session_id_id ON messages(session_id, id DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_messages_session_created ON messages(session_id, created_at DESC)")
            conn.commit()

    def ensure_session(self, session_id: str | None = None) -> str:
        sid = (session_id or str(uuid4())).strip()
        with connect_sqlite(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO sessions (session_id) VALUES (?)",
                (sid,),
            )
            conn.execute(
                "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
                (sid,),
            )
            conn.commit()
        return sid

    def add_message(self, session_id: str, role: str, content: str) -> None:
        trimmed = content[: settings.max_chat_message_chars]
        with connect_sqlite(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, trimmed),
            )
            conn.execute(
                "UPDATE sessions SET updated_at = CURRENT_TIMESTAMP WHERE session_id = ?",
                (session_id,),
            )
            conn.commit()

    def recent_messages(self, session_id: str, limit: int = 10) -> list[dict[str, Any]]:
        with connect_sqlite(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT role, content, created_at
                FROM messages
                WHERE session_id = ?
                ORDER BY id DESC
                LIMIT ?
                """,
                (session_id, limit),
            ).fetchall()
        rows.reverse()
        return [{"role": r[0], "content": r[1], "created_at": r[2]} for r in rows]

    def _first_user_message(self, conn, session_id: str) -> str:
        row = conn.execute(
            """
            SELECT content
            FROM messages
            WHERE session_id = ? AND role = 'user'
            ORDER BY id ASC
            LIMIT 1
            """,
            (session_id,),
        ).fetchone()
        return (row[0] if row else "Untitled session")[:80]

    def list_sessions(self, limit: int = 20) -> list[dict[str, Any]]:
        with connect_sqlite(self.db_path) as conn:
            rows = conn.execute(
                """
                SELECT
                    s.session_id,
                    s.created_at,
                    s.updated_at,
                    COUNT(m.id) AS message_count,
                    MAX(m.created_at) AS last_message_at
                FROM sessions s
                LEFT JOIN messages m ON m.session_id = s.session_id
                GROUP BY s.session_id, s.created_at, s.updated_at
                ORDER BY s.updated_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

            items = []
            for row in rows:
                items.append(
                    {
                        "session_id": row[0],
                        "created_at": row[1],
                        "updated_at": row[2],
                        "message_count": row[3],
                        "title": self._first_user_message(conn, row[0]),
                        "last_message_at": row[4],
                    }
                )
        return items

    def resolve_session_id(self, partial: str) -> str | None:
        needle = (partial or "").strip()
        if not needle:
            return None
        with connect_sqlite(self.db_path) as conn:
            exact = conn.execute(
                "SELECT session_id FROM sessions WHERE session_id = ?",
                (needle,),
            ).fetchone()
            if exact:
                return exact[0]

            rows = conn.execute(
                "SELECT session_id FROM sessions WHERE session_id LIKE ? ORDER BY updated_at DESC LIMIT 2",
                (f"{needle}%",),
            ).fetchall()
        if len(rows) == 1:
            return rows[0][0]
        return None

    def session_overview(self, session_id: str) -> dict[str, Any]:
        with connect_sqlite(self.db_path) as conn:
            session_row = conn.execute(
                "SELECT session_id, created_at, updated_at FROM sessions WHERE session_id = ?",
                (session_id,),
            ).fetchone()
            if not session_row:
                return {"ok": False, "error": f"Session not found: {session_id}"}

            stats_row = conn.execute(
                """
                SELECT
                    COUNT(*) AS message_count,
                    SUM(CASE WHEN role = 'user' THEN 1 ELSE 0 END) AS user_messages,
                    SUM(CASE WHEN role = 'assistant' THEN 1 ELSE 0 END) AS assistant_messages,
                    MAX(created_at) AS last_message_at
                FROM messages
                WHERE session_id = ?
                """,
                (session_id,),
            ).fetchone()
            title = self._first_user_message(conn, session_id)

        recent = self.recent_messages(session_id, limit=8)
        return {
            "ok": True,
            "session_id": session_row[0],
            "created_at": session_row[1],
            "updated_at": session_row[2],
            "message_count": stats_row[0] or 0,
            "user_messages": stats_row[1] or 0,
            "assistant_messages": stats_row[2] or 0,
            "title": title,
            "last_message_at": stats_row[3],
            "recent_messages": recent,
        }

    def _cleanup_candidates(
        self,
        keep_recent: int,
        drop_empty_older_than_days: int,
        drop_inactive_older_than_days: int,
    ) -> list[dict[str, Any]]:
        with connect_sqlite(self.db_path) as conn:
            keep_rows = conn.execute(
                "SELECT session_id FROM sessions ORDER BY updated_at DESC LIMIT ?",
                (keep_recent,),
            ).fetchall()
            keep_ids = {row[0] for row in keep_rows}

            rows = conn.execute(
                """
                SELECT
                    s.session_id,
                    s.created_at,
                    s.updated_at,
                    COUNT(m.id) AS message_count,
                    MAX(m.created_at) AS last_message_at
                FROM sessions s
                LEFT JOIN messages m ON m.session_id = s.session_id
                GROUP BY s.session_id, s.created_at, s.updated_at
                ORDER BY s.updated_at ASC
                """
            ).fetchall()

        items = []
        for row in rows:
            session_id = row[0]
            if session_id in keep_ids:
                continue
            message_count = row[3] or 0
            updated_at = row[2]
            candidate = {
                "session_id": session_id,
                "created_at": row[1],
                "updated_at": updated_at,
                "message_count": message_count,
                "last_message_at": row[4],
                "reason": None,
            }
            # simple string-based age comparison handled by SQLite ordering / timestamps
            if message_count == 0:
                candidate["reason"] = f"empty_older_than_{drop_empty_older_than_days}d"
                items.append(candidate)
                continue
            candidate["reason"] = f"inactive_older_than_{drop_inactive_older_than_days}d"
            items.append(candidate)
        return items

    def cleanup_sessions(
        self,
        keep_recent: int = 25,
        drop_empty_older_than_days: int = 7,
        drop_inactive_older_than_days: int = 90,
        dry_run: bool = False,
    ) -> dict[str, Any]:
        keep_recent = max(0, keep_recent)
        drop_empty_older_than_days = max(0, drop_empty_older_than_days)
        drop_inactive_older_than_days = max(0, drop_inactive_older_than_days)

        with connect_sqlite(self.db_path) as conn:
            keep_rows = conn.execute(
                "SELECT session_id FROM sessions ORDER BY updated_at DESC LIMIT ?",
                (keep_recent,),
            ).fetchall()
            keep_ids = {row[0] for row in keep_rows}

            all_rows = conn.execute(
                """
                SELECT
                    s.session_id,
                    s.created_at,
                    s.updated_at,
                    COUNT(m.id) AS message_count,
                    MAX(m.created_at) AS last_message_at
                FROM sessions s
                LEFT JOIN messages m ON m.session_id = s.session_id
                GROUP BY s.session_id, s.created_at, s.updated_at
                ORDER BY s.updated_at ASC
                """
            ).fetchall()

            candidates: list[dict[str, Any]] = []
            for row in all_rows:
                session_id = row[0]
                if session_id in keep_ids:
                    continue
                message_count = row[3] or 0
                updated_at = row[2]
                reason = None
                if message_count == 0:
                    cutoff_row = conn.execute(
                        "SELECT ? < datetime('now', ?) AS should_delete",
                        (updated_at, f"-{drop_empty_older_than_days} days"),
                    ).fetchone()
                    if cutoff_row and cutoff_row[0]:
                        reason = f"empty_older_than_{drop_empty_older_than_days}d"
                else:
                    cutoff_row = conn.execute(
                        "SELECT ? < datetime('now', ?) AS should_delete",
                        (updated_at, f"-{drop_inactive_older_than_days} days"),
                    ).fetchone()
                    if cutoff_row and cutoff_row[0]:
                        reason = f"inactive_older_than_{drop_inactive_older_than_days}d"
                if reason:
                    candidates.append(
                        {
                            "session_id": session_id,
                            "created_at": row[1],
                            "updated_at": updated_at,
                            "message_count": message_count,
                            "last_message_at": row[4],
                            "reason": reason,
                        }
                    )

            if dry_run:
                return {
                    "ok": True,
                    "dry_run": True,
                    "candidate_count": len(candidates),
                    "candidates": candidates[:100],
                    "plain_english": "This is the session cleanup preview. No data was deleted.",
                }

            deleted_session_ids = [item["session_id"] for item in candidates]
            for session_id in deleted_session_ids:
                conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
                conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            conn.commit()

        return {
            "ok": True,
            "dry_run": False,
            "deleted_count": len(deleted_session_ids),
            "deleted_session_ids": deleted_session_ids[:100],
            "plain_english": "JARVIS cleaned up older inactive or empty sessions based on the requested retention rules.",
            "next_action": "Open sessions again if you want to confirm the remaining session list.",
        }


memory_service = MemoryService()

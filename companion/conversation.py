"""대화 히스토리 저장소.

agent.md 2절에서 "결정 필요"로 남겨둔 저장 방식은 SQLite로 결정했다.
로컬 파일 하나로 오프라인에서 완결되고, 세션/시간 기준 조회가 쉬우며,
프로토타입 단계에 필요한 이상의 인프라(벡터 DB 등)를 요구하지 않는다.
"""
import sqlite3
import time
from pathlib import Path
from typing import Dict, List


class ConversationStore:
    def __init__(self, db_path: str, session_id: str = "default"):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id
        self.conn = sqlite3.connect(db_path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at REAL NOT NULL
            )
            """
        )
        self.conn.commit()

    def add(self, role: str, content: str) -> None:
        self.conn.execute(
            "INSERT INTO messages (session_id, role, content, created_at) VALUES (?, ?, ?, ?)",
            (self.session_id, role, content, time.time()),
        )
        self.conn.commit()

    def recent(self, limit: int) -> List[Dict[str, str]]:
        cur = self.conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (self.session_id, limit),
        )
        rows = cur.fetchall()
        rows.reverse()
        return [{"role": role, "content": content} for role, content in rows]

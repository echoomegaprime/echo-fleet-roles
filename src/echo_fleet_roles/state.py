from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class StateConflict(RuntimeError):
    """Raised when expected-current fencing detects a concurrent change."""


@dataclass(frozen=True)
class Transition:
    transition_id: int
    previous_role: str
    role: str
    changed: bool
    idempotency_key: str | None
    changed_at: str

    def as_dict(self) -> dict[str, Any]:
        return {
            "transition_id": self.transition_id,
            "previous_role": self.previous_role,
            "role": self.role,
            "changed": self.changed,
            "idempotency_key": self.idempotency_key,
            "changed_at": self.changed_at,
        }


def default_state_path() -> Path:
    if os.name == "nt":
        root = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return root / "EchoFleetRoles" / "state.sqlite3"
    root = Path(os.environ.get("XDG_STATE_HOME", Path.home() / ".local" / "state"))
    return root / "echo-fleet-roles" / "state.sqlite3"


class RoleState:
    def __init__(self, path: str | Path | None = None) -> None:
        self.path = Path(path) if path else default_state_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=15.0, isolation_level=None)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA busy_timeout=15000")
        connection.execute("PRAGMA foreign_keys=ON")
        return connection

    @contextmanager
    def _connection(self):
        connection = self._connect()
        try:
            yield connection
        finally:
            connection.close()

    def _initialize(self) -> None:
        with self._connection() as connection:
            connection.execute("PRAGMA journal_mode=WAL")
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS current_role (
                    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
                    role TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS transitions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    previous_role TEXT NOT NULL,
                    role TEXT NOT NULL,
                    changed INTEGER NOT NULL CHECK (changed IN (0, 1)),
                    idempotency_key TEXT UNIQUE,
                    metadata_json TEXT NOT NULL,
                    changed_at TEXT NOT NULL
                );
                """
            )

    def current(self, default_role: str) -> str:
        now = datetime.now(timezone.utc).isoformat()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute("SELECT role FROM current_role WHERE singleton=1").fetchone()
            if row is None:
                connection.execute(
                    "INSERT INTO current_role(singleton, role, updated_at) VALUES (1, ?, ?)",
                    (default_role, now),
                )
                role = default_role
            else:
                role = str(row["role"])
            connection.execute("COMMIT")
        return role

    def switch(
        self,
        role: str,
        default_role: str,
        *,
        expected_current: str | None = None,
        idempotency_key: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> Transition:
        now = datetime.now(timezone.utc).isoformat()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            if idempotency_key:
                prior = connection.execute(
                    "SELECT * FROM transitions WHERE idempotency_key=?", (idempotency_key,)
                ).fetchone()
                if prior is not None:
                    if str(prior["role"]) != role:
                        connection.execute("ROLLBACK")
                        raise StateConflict(
                            f"Idempotency key '{idempotency_key}' was already used for role '{prior['role']}'"
                        )
                    connection.execute("COMMIT")
                    return self._transition(prior)
            row = connection.execute("SELECT role FROM current_role WHERE singleton=1").fetchone()
            previous = str(row["role"]) if row else default_role
            if expected_current is not None and previous != expected_current:
                connection.execute("ROLLBACK")
                raise StateConflict(f"Expected current role '{expected_current}', found '{previous}'")
            changed = previous != role
            connection.execute(
                """INSERT INTO current_role(singleton, role, updated_at) VALUES (1, ?, ?)
                   ON CONFLICT(singleton) DO UPDATE SET role=excluded.role, updated_at=excluded.updated_at""",
                (role, now),
            )
            cursor = connection.execute(
                """INSERT INTO transitions(previous_role, role, changed, idempotency_key, metadata_json, changed_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (previous, role, int(changed), idempotency_key, json.dumps(metadata or {}, sort_keys=True), now),
            )
            record = connection.execute("SELECT * FROM transitions WHERE id=?", (cursor.lastrowid,)).fetchone()
            connection.execute("COMMIT")
        assert record is not None
        return self._transition(record)

    def history(self, limit: int = 20) -> list[Transition]:
        bounded = max(1, min(limit, 200))
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM transitions ORDER BY id DESC LIMIT ?", (bounded,)
            ).fetchall()
        return [self._transition(row) for row in rows]

    @staticmethod
    def _transition(row: sqlite3.Row) -> Transition:
        return Transition(
            transition_id=int(row["id"]),
            previous_role=str(row["previous_role"]),
            role=str(row["role"]),
            changed=bool(row["changed"]),
            idempotency_key=row["idempotency_key"],
            changed_at=str(row["changed_at"]),
        )

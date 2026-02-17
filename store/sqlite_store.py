# store/sqlite_store.py

import sqlite3
import json
from uuid import uuid4
from datetime import datetime, timezone

from model.entities import Case, CaseItem, BillingRecord, ActivitySummary
from model.enums import CaseItemKind, BillingDecision


class SQLiteStore:
    def __init__(self, db_path: str = "workflow.db"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    # --------------------------------------------------
    # Schema
    # --------------------------------------------------

    def _init_schema(self):
        cur = self.conn.cursor()

        cur.executescript("""
        CREATE TABLE IF NOT EXISTS cases (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            client_id TEXT,
            status TEXT NOT NULL,
            priority TEXT NOT NULL,
            attention_flags TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            due_at TEXT
        );

        CREATE TABLE IF NOT EXISTS case_items (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            kind TEXT NOT NULL,
            metadata TEXT NOT NULL,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS billing_records (
            id TEXT PRIMARY KEY,
            case_id TEXT NOT NULL,
            decision TEXT NOT NULL,
            decided_at TEXT NOT NULL,
            context TEXT NOT NULL
        );
        """)

        self.conn.commit()

    # --------------------------------------------------
    # Cases
    # --------------------------------------------------

    def add_case(self, case: Case):
        self.conn.execute(
            """
            INSERT INTO cases VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                case.id,
                case.title,
                case.client_id,
                case.status.value,
                case.priority.value,
                json.dumps([f.value for f in case.attention_flags]),
                case.created_at.isoformat(),
                case.updated_at.isoformat(),
                case.due_at.isoformat() if case.due_at else None,
            ),
        )
        self.conn.commit()

    def list_cases(self):
        rows = self.conn.execute("SELECT * FROM cases").fetchall()
        return [self._row_to_case(r) for r in rows]

    def get_case(self, case_id: str):
        row = self.conn.execute(
            "SELECT * FROM cases WHERE id = ?",
            (case_id,),
        ).fetchone()
        return self._row_to_case(row) if row else None

    def _row_to_case(self, r):
        from model.enums import WorkStatus, Priority, AttentionFlag

        case = Case(
            id=r["id"],
            title=r["title"],
            client_id=r["client_id"],
            status=WorkStatus(r["status"]),
            priority=Priority(r["priority"]),
            created_at=datetime.fromisoformat(r["created_at"]),
            updated_at=datetime.fromisoformat(r["updated_at"]),
            due_at=datetime.fromisoformat(r["due_at"]) if r["due_at"] else None,
        )
        case.attention_flags = {
            AttentionFlag(f) for f in json.loads(r["attention_flags"])
        }
        return case

    # --------------------------------------------------
    # Case Items (Timeline)
    # --------------------------------------------------

    def add_case_item(
        self,
        case_id: str,
        kind: CaseItemKind,
        ref_id: str | None = None,
        metadata: dict | None = None,
        created_at: datetime | None = None,
    ):
        self.conn.execute(
            """
            INSERT INTO case_items VALUES (?, ?, ?, ?, ?)
            """,
            (
                str(uuid4()),
                case_id,
                kind.value,
                json.dumps(metadata or {}),
                (created_at or datetime.now(timezone.utc)).isoformat(),
            ),
        )
        self.conn.commit()


    def list_case_items(self, case_id):
        rows = self.conn.execute(
            "SELECT * FROM case_items WHERE case_id = ? ORDER BY created_at",
            (case_id,),
        ).fetchall()

        return [
            CaseItem(
                id=r["id"],
                case_id=r["case_id"],
                kind=CaseItemKind(r["kind"]),
                metadata=json.loads(r["metadata"]),
                created_at=datetime.fromisoformat(r["created_at"]),
            )
            for r in rows
        ]

    # --------------------------------------------------
    # Billing
    # --------------------------------------------------

    def add_billing_record(self, record: BillingRecord):
        self.conn.execute(
            """
            INSERT INTO billing_records VALUES (?, ?, ?, ?, ?)
            """,
            (
                record.id,
                record.case_id,
                record.decision.value,
                record.decided_at.isoformat(),
                json.dumps(record.context),
            ),
        )
        self.conn.commit()

    def list_billing_records(self, case_id):
        rows = self.conn.execute(
            "SELECT * FROM billing_records WHERE case_id = ?",
            (case_id,),
        ).fetchall()

        return [
            BillingRecord(
                id=r["id"],
                case_id=r["case_id"],
                decision=BillingDecision(r["decision"]),
                decided_at=datetime.fromisoformat(r["decided_at"]),
                context=json.loads(r["context"]),
            )
            for r in rows
        ]

    # --------------------------------------------------
    # Activity / Agregados
    # --------------------------------------------------

    

    def get_activity_summary(self, case_id: str, since: datetime) -> ActivitySummary:
        summary = ActivitySummary(case_id=case_id, since=since)

        rows = self.conn.execute(
            """
            SELECT kind, metadata, created_at
            FROM case_items
            WHERE case_id = ?
            AND created_at >= ?
            """,
            (case_id, since.isoformat()),
        ).fetchall()

        for r in rows:
            kind = CaseItemKind(r["kind"])
            metadata = json.loads(r["metadata"]) if r["metadata"] else {}

            if kind == CaseItemKind.EMAIL:
                direction = metadata.get("direction")
                if direction == "inbound":
                    summary.inbound_emails += 1
                elif direction == "outbound":
                    summary.outbound_emails += 1

            elif kind == CaseItemKind.NOTE:
                summary.notes += 1

            elif kind == CaseItemKind.TASK:
                if metadata.get("completed"):
                    summary.tasks_completed += 1

        return summary

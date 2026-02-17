# store/protocol.py

from typing import Protocol, List, Optional
from datetime import datetime

from model.entities import Case, CaseItem, BillingRecord, ActivitySummary
from model.enums import CaseItemKind, BillingDecision


class StoreProtocol(Protocol):
    """
    Contrato semântico do Store.

    Define O QUE o sistema pode perguntar,
    não COMO os dados são guardados.
    """

    # -------------------------
    # CASES
    # -------------------------

    def add_case(self, case: Case) -> None: ...
    def get_case(self, case_id: str) -> Optional[Case]: ...
    def list_cases(self) -> List[Case]: ...

    # -------------------------
    # CASE ITEMS (timeline)
    # -------------------------

    def add_case_item(
        self,
        case_id: str,
        kind: CaseItemKind,
        ref_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        created_at: Optional[datetime] = None,
    ) -> CaseItem: ...

    def list_case_items(self, case_id: str) -> List[CaseItem]: ...

    # -------------------------
    # BILLING
    # -------------------------

    def add_billing_record(
        self,
        case: Case,
        decision: BillingDecision,
        context: Optional[dict] = None,
    ) -> BillingRecord: ...

    def list_billing_records(
        self,
        case_id: Optional[str] = None,
    ) -> List[BillingRecord]: ...

    # -------------------------
    # AGREGADOS / QUERIES
    # -------------------------

    def get_activity_summary(
        self,
        case_id: str,
        since: datetime,
    ) -> ActivitySummary: ...

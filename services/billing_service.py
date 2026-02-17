"""
BillingService

Executa a decisão do utilizador relativamente a faturação.

A decisão é humana, mas o registo é do sistema:
- cria BillingRecord
- cria CaseItem BILLING_EVENT
- limpa flags relevantes
"""

from datetime import datetime
from typing import Optional

from model.enums import BillingDecision, CaseItemKind
from store.inmemory import InMemoryStore


class BillingService:
    def __init__(self, store: InMemoryStore):
        self.store = store

    def apply_decision(
        self,
        case_id: str,
        decision: BillingDecision,
        context: Optional[dict] = None,
        now: Optional[datetime] = None,
    ):
        now = now or datetime.utcnow()
        context = context or {}

        case = self.store.get_case(case_id)
        if not case:
            raise ValueError(f"Case '{case_id}' não existe.")

        # 1) Registar a decisão como BillingRecord
        record = self.store.add_billing_record(
            case=case,
            decision=decision,
            context={**context, "decided_at": now.isoformat()},
        )

        # 2) Registar também na timeline do caso (CaseItem)
        self.store.add_case_item(
            case_id=case.id,
            kind=CaseItemKind.BILLING_EVENT,
            ref_id=record.id,
            metadata={
                "decision": decision.value,
                **context,
            },
        )

        return record

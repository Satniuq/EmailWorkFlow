"""
TESTE — CICLO COMPLETO DE BILLING

Objectivo:
- criar actividade significativa
- verificar BILLING_PENDING
- aplicar decisão humana
- verificar silêncio
"""

from datetime import timedelta

from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from model.enums import (
    CaseEventType,
    AttentionFlag,
    BillingDecision,
)
from model.entities import Case
from model.enums import WorkStatus, Priority


def banner(title):
    print("\n" + "=" * 90)
    print(title.center(90))
    print("=" * 90)


def test_billing_decision_flow():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    rules = RulesEngine(store, CaseStateMachine())

    case = Case(
        id="case-billing",
        title="Caso faturável",
        client_id="cliente@empresa.com",
        status=WorkStatus.IN_PROGRESS,
        priority=Priority.NORMAL,
        created_at=now,
        updated_at=now,
        due_at=None,
    )

    store.add_case(case)

    # --------------------------------------------------
    banner("CRIAR ACTIVIDADE SIGNIFICATIVA")

    rules.handle_event(
        case,
        CaseEventType.EMAIL_OUTBOUND,
        {"subject": "Trabalho feito"},
        now=now,
    )

    # Forçar janela de billing
    future = now + timedelta(days=1)
    rules.handle_event(case, CaseEventType.TIME_PASSED, now=future)

    assert AttentionFlag.BILLING_PENDING in case.attention_flags
    print("💰 Billing sugerido")

    # --------------------------------------------------
    banner("DECISÃO HUMANA — FATURAR")

    rules.handle_event(
        case,
        CaseEventType.USER_ACTION,
        {
            "action": "billing_decision",
            "decision": BillingDecision.TO_BILL,
        },
        now=future,
    )

    assert AttentionFlag.BILLING_PENDING not in case.attention_flags
    records = store.list_billing_records(case.id)
    assert len(records) == 1
    assert records[0].decision == BillingDecision.TO_BILL

    banner("✔️ TESTE PASSOU — BILLING FECHADO COM SILÊNCIO")


if __name__ == "__main__":
    test_billing_decision_flow()

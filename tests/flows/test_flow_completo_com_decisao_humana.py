"""
TESTE — FLOW COMPLETO COM UMA DECISÃO HUMANA

Objectivo:
- actividade significativa
- billing sugerido
- decisão humana
- silêncio
"""

from datetime import timedelta
from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from portals.attention import AttentionPortal
from model.entities import Case
from model.enums import (
    WorkStatus,
    Priority,
    CaseEventType,
    BillingDecision,
    AttentionFlag,
)


def banner(title):
    print("\n" + "=" * 100)
    print(title.center(100))
    print("=" * 100)


def test_flow_completo_com_decisao_humana():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    brain = RulesEngine(store, CaseStateMachine())
    attention = AttentionPortal()

    case = Case(
        id="flow-billing",
        title="Caso faturável",
        client_id="cliente@empresa.com",
        status=WorkStatus.IN_PROGRESS,
        priority=Priority.NORMAL,
        created_at=now,
        updated_at=now,
    )

    store.add_case(case)

    # --------------------------------------------------
    banner("ACTIVIDADE SIGNIFICATIVA")

    brain.handle_event(
        case,
        CaseEventType.EMAIL_OUTBOUND,
        {"subject": "Trabalho concluído"},
        now=now,
    )

    # --------------------------------------------------
    banner("SISTEMA AVALIA (TIME_PASSED)")

    later = now + timedelta(days=1)
    brain.handle_event(case, CaseEventType.TIME_PASSED, now=later)

    assert AttentionFlag.BILLING_PENDING in case.attention_flags
    print("💰 Billing pendente detectado")

    # --------------------------------------------------
    banner("DECISÃO HUMANA")

    brain.handle_event(
        case,
        CaseEventType.USER_ACTION,
        {
            "action": "billing_decision",
            "decision": BillingDecision.DONT_BILL,
        },
        now=later,
    )

    # --------------------------------------------------
    banner("RESULTADO FINAL")

    cards = attention.collect(store, later)
    assert not cards
    print("✔️ Decisão aplicada — silêncio restaurado")

    banner("FIM DO FLOW")

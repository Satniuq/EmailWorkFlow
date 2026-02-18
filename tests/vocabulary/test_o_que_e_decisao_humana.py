"""
TESTE — O QUE É DECISÃO HUMANA

Objectivo:
- definir que USER_ACTION fecha ciclos
- distinguir acção humana relevante vs irrelevante
"""

from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from model.entities import Case
from model.enums import (
    WorkStatus,
    Priority,
    CaseEventType,
    BillingDecision,
    AttentionFlag,
)
from datetime import timedelta


def banner(title):
    print("\n" + "=" * 90)
    print(title.center(90))
    print("=" * 90)


def test_o_que_e_decisao_humana():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    rules = RulesEngine(store, CaseStateMachine())

    case = Case(
        id="case-human",
        title="Teste decisão humana",
        client_id="cliente@empresa.com",
        status=WorkStatus.IN_PROGRESS,
        priority=Priority.NORMAL,
        created_at=now,
        updated_at=now,
    )

    store.add_case(case)

    # --------------------------------------------------
    banner("SISTEMA SUGERE BILLING")

    rules.handle_event(
        case,
        CaseEventType.EMAIL_OUTBOUND,
        {"subject": "Trabalho feito"},
        now=now,
    )

    later = now + timedelta(days=1)
    rules.handle_event(case, CaseEventType.TIME_PASSED, now=later)

    assert AttentionFlag.BILLING_PENDING in case.attention_flags

    # --------------------------------------------------
    banner("DECISÃO HUMANA RELEVANTE")

    rules.handle_event(
        case,
        CaseEventType.USER_ACTION,
        {
            "action": "billing_decision",
            "decision": BillingDecision.DONT_BILL
        },
        now=later,
    )

    assert AttentionFlag.BILLING_PENDING not in case.attention_flags
    print("🧠 Decisão humana fecha ciclo")

    banner("✔️ DECISÃO HUMANA DEFINIDA")

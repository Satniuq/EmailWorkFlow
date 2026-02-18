"""
TESTE — MESMO INPUT, MESMO RESULTADO

Objectivo:
- proteger comportamento contra refactors
"""

from datetime import timedelta
from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from model.entities import Case
from model.enums import WorkStatus, Priority, CaseEventType


def banner(title):
    print("\n" + "=" * 90)
    print(title.center(90))
    print("=" * 90)


def test_mesmo_input_mesmo_resultado():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    rules = RulesEngine(store, CaseStateMachine())

    case = Case(
        id="case-regression",
        title="Regressão",
        client_id="cliente@empresa.com",
        status=WorkStatus.IN_PROGRESS,
        priority=Priority.NORMAL,
        created_at=now,
        updated_at=now,
    )

    store.add_case(case)

    # sequência fixa
    rules.handle_event(case, CaseEventType.EMAIL_OUTBOUND, {}, now=now)
    t1 = now + timedelta(days=8)
    rules.handle_event(case, CaseEventType.TIME_PASSED, now=t1)

    snapshot = set(case.attention_flags)

    # repetir exactamente a mesma sequência
    rules.handle_event(case, CaseEventType.TIME_PASSED, now=t1)

    assert snapshot == set(case.attention_flags)

    banner("✔️ RESULTADO DETERMINÍSTICO")

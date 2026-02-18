"""
TESTE — RULES ENGINE IDEMPOTENTE

Objectivo:
- garantir que múltiplos TIME_PASSED não acumulam efeitos
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


def test_rules_engine_idempotente():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    rules = RulesEngine(store, CaseStateMachine())

    case = Case(
        id="case-idem",
        title="Idempotência",
        client_id="cliente@empresa.com",
        status=WorkStatus.IN_PROGRESS,
        priority=Priority.NORMAL,
        created_at=now,
        updated_at=now,
    )

    store.add_case(case)

    # --------------------------------------------------
    banner("TIME_PASSED REPETIDO")

    for i in range(5):
        rules.handle_event(
            case,
            CaseEventType.TIME_PASSED,
            now=now + timedelta(days=10),
        )

    items = store.list_case_items(case.id)

    assert len(items) == 0

    banner("✔️ TIME_PASSED É IDEMPOTENTE")

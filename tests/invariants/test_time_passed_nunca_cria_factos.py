"""
TESTE — TIME_PASSED NUNCA CRIA FACTOS

Objectivo:
- garantir que TIME_PASSED não cria CaseItems
- proteger refactorizações futuras
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


def test_time_passed_nunca_cria_factos():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    rules = RulesEngine(store, CaseStateMachine())

    case = Case(
        id="case-time",
        title="Caso temporal",
        client_id="cliente@empresa.com",
        status=WorkStatus.IN_PROGRESS,
        priority=Priority.NORMAL,
        created_at=now,
        updated_at=now,
    )

    store.add_case(case)

    initial_items = store.list_case_items(case.id)

    # --------------------------------------------------
    banner("PASSAGEM DE TEMPO (30 DIAS)")

    future = now + timedelta(days=30)
    rules.handle_event(case, CaseEventType.TIME_PASSED, now=future)

    final_items = store.list_case_items(case.id)

    assert len(initial_items) == len(final_items)

    banner("✔️ TIME_PASSED NÃO CRIOU FACTOS")

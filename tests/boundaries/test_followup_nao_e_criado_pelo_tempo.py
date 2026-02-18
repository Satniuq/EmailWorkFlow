"""
TESTE — FOLLOW-UP NÃO NASCE DO TEMPO

Objectivo:
- garantir que TIME_PASSED nunca cria follow-ups
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


def test_followup_nao_e_criado_pelo_tempo():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    rules = RulesEngine(store, CaseStateMachine())

    case = Case(
        id="case-followup",
        title="Teste follow-up",
        client_id="cliente@empresa.com",
        status=WorkStatus.IN_PROGRESS,
        priority=Priority.NORMAL,
        created_at=now,
        updated_at=now,
        due_at=None,
    )

    store.add_case(case)

    future = now + timedelta(days=60)
    rules.handle_event(case, CaseEventType.TIME_PASSED, now=future)

    assert case.due_at is None

    banner("✔️ FOLLOW-UP NÃO É CRIADO PELO TEMPO")

"""
TESTE — FLAGS NUNCA MUDAM ESTADO

Objectivo:
- garantir que atenção não altera status
"""

from datetime import timedelta
from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from model.entities import Case
from model.enums import WorkStatus, Priority, CaseEventType, AttentionFlag


def banner(title):
    print("\n" + "=" * 90)
    print(title.center(90))
    print("=" * 90)


def test_flags_nunca_mudam_estado():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    rules = RulesEngine(store, CaseStateMachine())

    case = Case(
        id="case-flags",
        title="Flags não mudam estado",
        client_id="cliente@empresa.com",
        status=WorkStatus.IN_PROGRESS,
        priority=Priority.NORMAL,
        created_at=now,
        updated_at=now,
        due_at=now - timedelta(days=1),
    )

    store.add_case(case)

    # --------------------------------------------------
    banner("ACTIVIDADE INICIAL")

    rules.handle_event(
        case,
        CaseEventType.EMAIL_OUTBOUND,
        {"subject": "Primeira resposta"},
        now=now,
    )

    # --------------------------------------------------
    banner("PASSAGEM DE TEMPO")

    future = now + timedelta(days=10)
    rules.handle_event(case, CaseEventType.TIME_PASSED, now=future)

    assert AttentionFlag.OVERDUE in case.attention_flags
    assert AttentionFlag.STALE in case.attention_flags
    assert case.status == WorkStatus.IN_PROGRESS

    banner("✔️ FLAGS NÃO ALTERAM ESTADO")


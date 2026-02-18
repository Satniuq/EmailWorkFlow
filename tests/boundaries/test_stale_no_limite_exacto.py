"""
TESTE — STALE NO LIMITE EXACTO

Objectivo:
- definir comportamento no limite temporal
- evitar ambiguidade futura
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


def test_stale_no_limite_exacto():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    rules = RulesEngine(store, CaseStateMachine())

    case = Case(
        id="case-stale",
        title="Teste STALE",
        client_id="cliente@empresa.com",
        status=WorkStatus.IN_PROGRESS,
        priority=Priority.NORMAL,
        created_at=now,
        updated_at=now,
    )

    store.add_case(case)

    # --------------------------------------------------
    banner("TIME_PASSED — EXACTAMENTE 7 DIAS")

    t1 = now + timedelta(days=7)
    # criar actividade inicial
    rules.handle_event(
        case,
        CaseEventType.EMAIL_OUTBOUND,
        event_context={"subject": "Primeira resposta"},
        now=now,
)


    assert AttentionFlag.STALE not in case.attention_flags
    print("🧠 Ainda NÃO está STALE")

    # --------------------------------------------------
    banner("TIME_PASSED — 7 DIAS + 1 SEGUNDO")

    t2 = t1 + timedelta(seconds=1)
    rules.handle_event(case, CaseEventType.TIME_PASSED, now=t2)

    assert AttentionFlag.STALE in case.attention_flags
    print("🧠 Agora está STALE")

    banner("✔️ LIMITE DE STALE DEFINIDO")

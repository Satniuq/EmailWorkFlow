"""
TESTE — O QUE É ACTIVIDADE SIGNIFICATIVA

Objectivo:
- definir que tipos de eventos contam como actividade
- proteger STALE, billing e silêncio
"""

from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from model.entities import Case
from model.enums import WorkStatus, Priority, CaseEventType, AttentionFlag
from datetime import timedelta


def banner(title):
    print("\n" + "=" * 90)
    print(title.center(90))
    print("=" * 90)


def test_o_que_e_atividade_significativa():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    rules = RulesEngine(store, CaseStateMachine())

    case = Case(
        id="case-activity",
        title="Teste actividade",
        client_id="cliente@empresa.com",
        status=WorkStatus.IN_PROGRESS,
        priority=Priority.NORMAL,
        created_at=now,
        updated_at=now,
    )

    store.add_case(case)

    # --------------------------------------------------
    banner("RUÍDO — TIME_PASSED NÃO CONTA")

    future = now + timedelta(days=10)
    rules.handle_event(case, CaseEventType.TIME_PASSED, now=future)

    assert AttentionFlag.STALE not in case.attention_flags
    print("🧠 TIME_PASSED não é actividade")

    # --------------------------------------------------
    banner("ACTIVIDADE — EMAIL OUTBOUND")

    rules.handle_event(
        case,
        CaseEventType.EMAIL_OUTBOUND,
        {"subject": "Resposta enviada"},
        now=future,
    )

    later = future + timedelta(days=8)
    rules.handle_event(case, CaseEventType.TIME_PASSED, now=later)

    assert AttentionFlag.STALE in case.attention_flags
    print("🧠 EMAIL_OUTBOUND conta como actividade")

    banner("✔️ ACTIVIDADE SIGNIFICATIVA DEFINIDA")

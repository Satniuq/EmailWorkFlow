"""
TESTE — EMAIL OUTBOUND CRIA FOLLOW-UP AUTOMÁTICO

Objectivo:
- enviar email outbound
- confirmar que é criado um due_at futuro
- confirmar que NÃO há flags imediatas
"""

from datetime import timedelta

from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from model.enums import CaseEventType, AttentionFlag


def banner(title):
    print("\n" + "=" * 90)
    print(title.center(90))
    print("=" * 90)


def test_email_outbound_creates_followup():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    rules = RulesEngine(store, CaseStateMachine())

    # Criar caso manualmente
    from model.entities import Case
    from model.enums import WorkStatus, Priority

    case = Case(
        id="case-1",
        title="Follow-up test",
        client_id="cliente@empresa.com",
        status=WorkStatus.IN_PROGRESS,
        priority=Priority.NORMAL,
        created_at=now,
        updated_at=now,
        due_at=None,
    )

    store.add_case(case)

    # --------------------------------------------------
    banner("EMAIL OUTBOUND")

    rules.handle_event(
        case,
        CaseEventType.EMAIL_OUTBOUND,
        event_context={"subject": "Re: Follow-up"},
        now=now,
    )

    assert case.due_at is not None
    assert case.due_at > now

    print(f"📅 follow-up criado para: {case.due_at}")

    # Não deve haver atenção imediata
    assert AttentionFlag.OVERDUE not in case.attention_flags
    assert AttentionFlag.STALE not in case.attention_flags

    banner("✔️ TESTE PASSOU — FOLLOW-UP AUTOMÁTICO CRIADO")


if __name__ == "__main__":
    test_email_outbound_creates_followup()

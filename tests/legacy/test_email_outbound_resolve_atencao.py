"""
TESTE — EMAIL OUTBOUND RESOLVE STALE E OVERDUE

Objectivo:
- criar um caso com atraso e estagnação
- confirmar que aparecem flags
- enviar EMAIL_OUTBOUND
- confirmar que as flags desaparecem automaticamente
"""

from datetime import timedelta

from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from services.email_ingestion_service import EmailIngestionService
from model.enums import CaseEventType, AttentionFlag


def banner(title):
    print("\n" + "=" * 90)
    print(title.center(90))
    print("=" * 90)


def dump_flags(case, label):
    flags = ", ".join(f.name for f in case.attention_flags) or "nenhuma"
    print(f"🧠 {label} → flags: {flags}")


def test_email_outbound_resolve_atencao():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    rules = RulesEngine(store, CaseStateMachine())
    ingestion = EmailIngestionService(store, rules, clock)

    # --------------------------------------------------
    banner("CRIAR CASO (EMAIL INBOUND)")

    ingestion.ingest({
        "message_id": "in-001",
        "thread_id": "thread-test",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Assunto com prazo",
        "body": "Precisamos disto resolvido.",
    })

    case = store.list_cases()[0]

    # Forçar atraso
    case.due_at = now - timedelta(days=1)

    # --------------------------------------------------
    banner("PASSAGEM DE TEMPO (8 DIAS) → STALE + OVERDUE")

    future = now + timedelta(days=8)
    rules.handle_event(case, CaseEventType.TIME_PASSED, now=future)

    dump_flags(case, "ANTES DO EMAIL")

    assert AttentionFlag.OVERDUE in case.attention_flags
    assert AttentionFlag.STALE in case.attention_flags

    # --------------------------------------------------
    banner("ENVIO DE EMAIL OUTBOUND")

    rules.handle_event(
        case,
        CaseEventType.EMAIL_OUTBOUND,
        {
            "message_id": "out-001",
            "thread_id": "thread-test",
            "to": ["cliente@empresa.com"],
            "subject": "Re: Assunto com prazo",
        },
        now=future,
    )

    dump_flags(case, "DEPOIS DO EMAIL")

    assert AttentionFlag.OVERDUE not in case.attention_flags
    assert AttentionFlag.STALE not in case.attention_flags

    banner("✔️ TESTE PASSOU — EMAIL RESOLVE ATENÇÃO")


if __name__ == "__main__":
    test_email_outbound_resolve_atencao()

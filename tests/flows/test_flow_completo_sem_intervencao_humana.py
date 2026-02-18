"""
TESTE — FLOW COMPLETO SEM INTERVENÇÃO HUMANA

Objectivo:
- EMAIL_INBOUND
- resposta tua
- passagem de tempo
- silêncio absoluto
"""

from datetime import timedelta
from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from services.email_ingestion_service import EmailIngestionService
from portals.attention import AttentionPortal
from model.enums import CaseEventType


def banner(title):
    print("\n" + "=" * 100)
    print(title.center(100))
    print("=" * 100)


def test_flow_completo_sem_intervencao_humana():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    store = InMemoryStore()
    brain = RulesEngine(store, CaseStateMachine())
    ingestion = EmailIngestionService(store, brain, clock)
    attention = AttentionPortal()

    now = clock.now()

    # --------------------------------------------------
    banner("EMAIL INBOUND (CLIENTE)")

    ingestion.ingest({
        "message_id": "flow-001",
        "thread_id": "flow-thread",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Pedido simples",
        "body": "Pode confirmar este ponto?",
    })

    case = store.list_cases()[0]

    # --------------------------------------------------
    banner("RESPOSTA TUA")

    now = now + timedelta(hours=2)
    brain.handle_event(
        case,
        CaseEventType.EMAIL_OUTBOUND,
        {"subject": "Re: Pedido simples"},
        now=now,
    )

    # --------------------------------------------------
    banner("PASSAGEM DE TEMPO (15 DIAS)")

    now = now + timedelta(days=15)
    cards = attention.collect(store, now)

    # --------------------------------------------------
    banner("RESULTADO FINAL")

    assert not cards
    print("✔️ Nenhuma atenção gerada — silêncio correcto")

    banner("FIM DO FLOW")

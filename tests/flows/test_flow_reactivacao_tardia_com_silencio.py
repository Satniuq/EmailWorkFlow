"""
TESTE — FLOW DE REACTIVAÇÃO TARDIA

Objectivo:
- caso antigo
- silêncio prolongado
- novo email
- continuidade correcta
- sem ruído artificial
"""

from datetime import timedelta
from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from services.email_ingestion_service import EmailIngestionService
from portals.attention import AttentionPortal


def banner(title):
    print("\n" + "=" * 100)
    print(title.center(100))
    print("=" * 100)


def test_flow_reactivacao_tardia_com_silencio():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    store = InMemoryStore()
    brain = RulesEngine(store, CaseStateMachine())
    ingestion = EmailIngestionService(store, brain, clock)
    attention = AttentionPortal()

    now = clock.now()

    # --------------------------------------------------
    banner("EMAIL ORIGINAL")

    ingestion.ingest({
        "message_id": "old-001",
        "thread_id": "long-thread",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Processo antigo",
        "body": "Ponto de situação.",
    })

    case = store.list_cases()[0]

    # --------------------------------------------------
    banner("SILÊNCIO (90 DIAS)")

    now = now + timedelta(days=90)
    cards = attention.collect(store, now)
    assert not cards
    print("🧠 Nenhuma atenção durante silêncio")

    # --------------------------------------------------
    banner("EMAIL TARDIO")

    ingestion.ingest({
        "message_id": "old-002",
        "thread_id": "long-thread",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Re: Processo antigo",
        "body": "Voltamos a este tema.",
    })

    # --------------------------------------------------
    banner("RESULTADO FINAL")

    assert len(store.list_cases()) == 1
    cards = attention.collect(store, now)
    assert not cards

    print("✔️ Continuidade aplicada sem ruído")

    banner("FIM DO FLOW")

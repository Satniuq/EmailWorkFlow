"""
TESTE — REATIVAÇÃO TARDIA

Objectivo:
- provar que um caso antigo reaparece correctamente
"""

from datetime import timedelta
from services.clock import Clock

from store.sqlite_store import SQLiteStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from services.email_ingestion_service import EmailIngestionService
from portals.attention import AttentionPortal


def banner(title):
    print("\n" + "=" * 90)
    print(title.center(90))
    print("=" * 90)


def test_reativacao():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    store = SQLiteStore(":memory:")
    brain = RulesEngine(store, CaseStateMachine())
    ingestion = EmailIngestionService(store, brain, clock)
    attention = AttentionPortal()

    now = clock.now()

    # --------------------------------------------------
    banner("CASO ORIGINAL")

    ingestion.ingest({
        "message_id": "r1",
        "thread_id": "long-thread",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Processo antigo",
        "body": "Segue ponto da situação.",
    })

    case = store.list_cases()[0]

    # --------------------------------------------------
    banner("SILÊNCIO (60 DIAS)")

    now = now + timedelta(days=60)

    # --------------------------------------------------
    banner("EMAIL TARDO")

    ingestion.ingest({
        "message_id": "r2",
        "thread_id": "long-thread",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Re: Processo antigo",
        "body": "Voltamos a este tema.",
    })

    banner("ESTADO FINAL")

    print(f"\n📦 Total de casos: {len(store.list_cases())}")
    print(f"📂 Caso único: {case.title}")
    print(f"🧠 Timeline: {len(store.list_case_items(case.id))} itens")

    banner("FIM DO TESTE")


if __name__ == "__main__":
    test_reativacao()

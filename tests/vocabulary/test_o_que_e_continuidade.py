"""
TESTE — O QUE É CONTINUIDADE

Objectivo:
- definir formalmente quando existe continuidade
- garantir que continuidade depende de contexto, não de tempo
"""

from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from services.email_ingestion_service import EmailIngestionService


def banner(title):
    print("\n" + "=" * 90)
    print(title.center(90))
    print("=" * 90)


def test_o_que_e_continuidade():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    store = InMemoryStore()
    brain = RulesEngine(store, CaseStateMachine())
    ingestion = EmailIngestionService(store, brain, clock)

    # --------------------------------------------------
    banner("EMAIL BASE")

    ingestion.ingest({
        "message_id": "c-001",
        "thread_id": "thread-continuidade",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Contrato A",
        "body": "Segue contrato.",
    })

    assert len(store.list_cases()) == 1
    case = store.list_cases()[0]

    # --------------------------------------------------
    banner("EMAIL RESPOSTA — MESMO THREAD")

    ingestion.ingest({
        "message_id": "c-002",
        "thread_id": "thread-continuidade",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Re: Contrato A",
        "body": "Alguma novidade?",
    })

    assert len(store.list_cases()) == 1
    assert store.list_cases()[0].id == case.id

    banner("✔️ CONTINUIDADE DEFINIDA POR THREAD_ID")

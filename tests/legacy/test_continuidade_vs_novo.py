"""
TESTE — CONTINUIDADE VS NOVO CASO

Objectivo:
- provar quando o sistema aplica continuidade
- provar quando NÃO aplica
"""

from datetime import timedelta
from services.clock import Clock

from store.sqlite_store import SQLiteStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from services.email_ingestion_service import EmailIngestionService


def banner(title):
    print("\n" + "=" * 90)
    print(title.center(90))
    print("=" * 90)


def dump_cases(store):
    print(f"\n📦 Total de casos: {len(store.list_cases())}")
    for c in store.list_cases():
        print(f" - {c.title} | id={c.id}")


def test_continuidade_vs_novo():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    store = SQLiteStore(":memory:")
    brain = RulesEngine(store, CaseStateMachine())
    ingestion = EmailIngestionService(store, brain, clock)

    now = clock.now()

    # --------------------------------------------------
    banner("CRIAR CASO BASE")

    ingestion.ingest({
        "message_id": "base-001",
        "thread_id": "thread-x",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Contrato X",
        "body": "Segue contrato.",
    })

    dump_cases(store)

    # --------------------------------------------------
    banner("CENÁRIO A — CONTINUIDADE (thread_id)")

    ingestion.ingest({
        "message_id": "reply-001",
        "thread_id": "thread-x",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Re: Contrato X",
        "body": "Alguma novidade?",
    })

    dump_cases(store)

    # --------------------------------------------------
    banner("CENÁRIO B — SEM CONTINUIDADE (assunto diferente)")

    ingestion.ingest({
        "message_id": "new-001",
        "thread_id": None,
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Outro assunto",
        "body": "Podemos falar?",
    })

    dump_cases(store)

    banner("FIM DO TESTE")
    


if __name__ == "__main__":
    test_continuidade_vs_novo()

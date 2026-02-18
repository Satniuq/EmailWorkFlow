"""
TESTE — EMAIL JURÍDICO REAL (RESOLUTION 4)

Simula a recepção de um email jurídico longo, formal,
com histórico, CCs e risco reputacional.

Objectivo:
Ver exactamente o que o sistema faz — e o que NÃO faz.
"""

from datetime import timedelta

from services.clock import Clock
from store.sqlite_store import SQLiteStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from services.email_ingestion_service import EmailIngestionService

from model.enums import CaseEventType


# ---------------------------------------------------------------------
# Logging utilitário
# ---------------------------------------------------------------------

def banner(title):
    print("\n" + "=" * 100)
    print(title.center(100))
    print("=" * 100 + "\n")


def dump_case(store, case):
    print(f"📂 CASO: {case.title}")
    print(f"   id: {case.id}")
    print(f"   priority: {case.priority.value}")
    print(f"   status: {case.status.value}")
    print(f"   attention_flags: {[f.value for f in case.attention_flags]}")
    print("   timeline:")
    for item in store.list_case_items(case.id):
        meta = ", ".join(f"{k}={v}" for k, v in item.metadata.items())
        print(f"     • {item.created_at.isoformat()} | {item.kind.value} | {meta}")
    print()


# ---------------------------------------------------------------------
# Teste principal
# ---------------------------------------------------------------------

def test_email_juridico_real():
    banner("INICIALIZAÇÃO DO SISTEMA")

    clock = Clock()
    store = SQLiteStore(":memory:")
    sm = CaseStateMachine()
    brain = RulesEngine(store, sm)
    ingestion = EmailIngestionService(store, brain, clock)

    now = clock.now()
    print(f"⏱️  TEMPO INICIAL → {now.isoformat()}")

    # --------------------------------------------------
    banner("CRIAR CASO BASE (HISTÓRICO EXISTENTE)")

    ingestion.ingest({
        "message_id": "r4-001",
        "thread_id": "resolution-4",
        "from": "peter@abbeygate.pt",
        "to": ["jose.quintas@mga.com.pt"],
        "cc": ["giovanni.campus@multiserass.com"],
        "subject": "Resolution 4",
        "body": "Please see the attached minutes for signature.",
    })

    case = store.list_cases()[0]
    dump_case(store, case)

    # --------------------------------------------------
    banner("EMAIL JURÍDICO REAL RECEBIDO (RESPOSTA)")

    now = now + timedelta(days=200)

    ingestion.ingest({
        "message_id": "r4-002",
        "thread_id": "resolution-4",
        "from": "marco.pinta@msamizar.com",
        "to": ["peter@abbeygate.pt"],
        "cc": [
            "jose.quintas@mga.com.pt",
            "giovanni.campus@multiserass.com",
        ],
        "subject": "Re: Resolution 4",
        "body": """
Dear Peter,

First of all, we apologize for the inconvenience and will do our best
to clarify what happened.

Following a discussion with my colleagues who managed the process
leading to the disposal of MSA Portugal’s activities, it appears that
both the handover of the claims and the related funds were agreed with
the company.

We kindly ask for a few days to gather the requested documentation
and provide you with a clear update on the situation.

Thank you.
""",
    })

    # --------------------------------------------------
    banner("ESTADO FINAL DO SISTEMA")

    print(f"📦 Total de casos no sistema: {len(store.list_cases())}")
    dump_case(store, case)

    banner("FIM DO TESTE")


# ---------------------------------------------------------------------

if __name__ == "__main__":
    test_email_juridico_real()

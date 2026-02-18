"""
TESTE — SILÊNCIO INTELIGENTE

Objectivo:
- garantir que após resposta tua
- e ausência de novos sinais
- o sistema NÃO gera atenção artificial
"""

from datetime import timedelta
from services.clock import Clock

from store.sqlite_store import SQLiteStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from services.email_ingestion_service import EmailIngestionService
from portals.attention import AttentionPortal
from model.enums import CaseEventType


# ---------------------------------------------------------------------
# UTILITÁRIOS
# ---------------------------------------------------------------------

def banner(title):
    print("\n" + "=" * 90)
    print(title.center(90))
    print("=" * 90)


# ---------------------------------------------------------------------
# TESTE
# ---------------------------------------------------------------------

def test_silencio_inteligente():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    store = SQLiteStore(":memory:")
    brain = RulesEngine(store, CaseStateMachine())
    ingestion = EmailIngestionService(store, brain, clock)
    attention_portal = AttentionPortal()

    now = clock.now()
    print(f"\n⏱️  TEMPO INICIAL → {now.isoformat()}")

    # --------------------------------------------------
    banner("EMAIL INBOUND (CLIENTE)")

    ingestion.ingest({
        "message_id": "sil-001",
        "thread_id": "silence-thread",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Questão jurídica",
        "body": "Precisamos de ajuda com um tema.",
    })

    case = store.list_cases()[0]

    # --------------------------------------------------
    banner("RESPOSTA TUA")

    now = now + timedelta(days=1)

    brain.handle_event(
        case=case,
        event_type=CaseEventType.EMAIL_OUTBOUND,
        event_context={
            "subject": "Re: Questão jurídica",
        },
        now=now,
    )

    print("🧠 Resposta enviada")
    print(f"   • case_id: {case.id}")

    # --------------------------------------------------
    banner("PASSAGEM DE TEMPO (14 DIAS)")

    now = now + timedelta(days=14)
    print(f"\n⏱️  TEMPO ATUAL → {now.isoformat()}")

    cards = attention_portal.collect(store, now)

    banner("RESULTADO")

    if not cards:
        print("✔️ Nenhum cartão de atenção — silêncio correcto")
    else:
        print("❌ Atenção indevida gerada:")
        for c in cards:
            print(c)

    banner("FIM DO TESTE")


# ---------------------------------------------------------------------

if __name__ == "__main__":
    test_silencio_inteligente()

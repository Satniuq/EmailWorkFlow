"""
TESTE DE JORNADA COMPLETA DE RELAÇÃO POR EMAIL

Este teste simula:
- vida pessoal
- ambiguidade inicial
- evolução para relação profissional
- actividade continuada
- billing
- silêncio
- auditoria final

O objectivo é VER e COMPREENDER tudo a acontecer.
"""

from datetime import timedelta
from services.clock import Clock

from store.sqlite_store import SQLiteStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from services.email_ingestion_service import EmailIngestionService
from services.billing_service import BillingService

from portals.billing import BillingPortal
from portals.attention import AttentionPortal
from portals.classification import ClassificationPortal
from dashboard.renderer import DashboardRenderer

from model.enums import BillingDecision, CaseEventType


# ---------------------------------------------------------------------
# UTILITÁRIOS DE LOGGING (NARRATIVO)
# ---------------------------------------------------------------------

def banner(title: str):
    print("\n" + "=" * 90)
    print(f" {title} ".center(90, "="))
    print("=" * 90 + "\n")


def log_event(title: str, payload: dict | None = None):
    print(f"\n🧠 {title}")
    if payload:
        for k, v in payload.items():
            print(f"   • {k}: {v}")


def log_time(now):
    print(f"\n⏱️  TEMPO ATUAL → {now.isoformat()}")


def dump_store_verbose(store):
    print("\n📦 AUDITORIA COMPLETA DO STORE\n")

    for case in store.list_cases():
        print("─" * 70)
        print(f"📂 Caso: {case.title}")
        print(f"   id: {case.id}")
        print(f"   priority: {case.priority.value}")
        print(f"   status: {case.status.value}")
        print(f"   attention_flags: {[f.value for f in case.attention_flags]}")

        items = store.list_case_items(case.id)
        print(f"   timeline ({len(items)} itens):")

        for item in items:
            meta = ", ".join(f"{k}={v}" for k, v in item.metadata.items())
            print(
                f"     • {item.created_at.isoformat()} | "
                f"{item.kind.value.upper()} | {meta}"
            )

        print()


def assert_store_contract(store, clock):
    """
    Garante que o Store cumpre o contrato mínimo esperado
    pelo RulesEngine e pelos Portais.
    """
    cases = store.list_cases()
    if not cases:
        return

    case = cases[0]
    summary = store.get_activity_summary(case.id, clock.now() - timedelta(days=30))

    assert hasattr(summary, "is_significant"), \
        "ActivitySummary não cumpre o contrato (falta is_significant())"


# ---------------------------------------------------------------------
# TESTE PRINCIPAL
# ---------------------------------------------------------------------

def test_jornada_completa():
    banner("INICIALIZAÇÃO DO SISTEMA")

    clock = Clock()
    store = SQLiteStore(":memory:")
    sm = CaseStateMachine()
    brain = RulesEngine(store, sm)
    ingestion = EmailIngestionService(store, brain, clock)
    billing_service = BillingService(store)

    attention_portal = AttentionPortal()
    billing_portal = BillingPortal()
    classification_portal = ClassificationPortal()
    dashboard = DashboardRenderer()

    now = clock.now()
    log_time(now)

    # --------------------------------------------------
    banner("DIA 1 — EMAIL PESSOAL")

    ingestion.ingest({
        "message_id": "p1",
        "thread_id": None,
        "from": "amigo@gmail.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Jantar sexta?",
        "body": "Bora combinar qualquer coisa?",
    })

    log_event("Email pessoal ingerido", {
        "casos_existentes": len(store.list_cases()),
    })

    # --------------------------------------------------
    banner("DIA 2 — CONTACTO AMBÍGUO")

    now = now + timedelta(days=1)
    log_time(now)

    ingestion.ingest({
        "message_id": "a1",
        "thread_id": None,
        "from": "contacto@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Olá",
        "body": "Podemos falar?",
    })

    log_event("Contacto ambíguo ingerido", {
        "casos_existentes": len(store.list_cases()),
    })

    # --------------------------------------------------
    banner("DIA 3 — EMAIL PROFISSIONAL INICIAL")

    now = now + timedelta(days=1)
    log_time(now)

    ingestion.ingest({
        "message_id": "b1",
        "thread_id": "t-phoenix",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Contrato Projeto Phoenix",
        "body": "Segue o contrato para análise.",
    })

    phoenix = next(c for c in store.list_cases() if "Phoenix" in c.title)

    log_event("Caso profissional criado", {
        "case_id": phoenix.id,
        "priority": phoenix.priority.value,
        "status": phoenix.status.value,
    })

    # --------------------------------------------------
    banner("DIA 4 — RESPOSTA TUA")

    now = now + timedelta(days=1)
    log_time(now)

    brain.handle_event(
        case=phoenix,
        event_type=CaseEventType.EMAIL_OUTBOUND,
        event_context={"subject": "Re: Contrato Projeto Phoenix"},
        now=now,
    )

    log_event("Resposta enviada", {
        "case": phoenix.title,
        "attention_flags": [f.value for f in phoenix.attention_flags],
    })

    # --------------------------------------------------
    banner("DIA 7 — FOLLOW-UP DO CLIENTE")

    now = now + timedelta(days=3)
    log_time(now)

    ingestion.ingest({
        "message_id": "b2",
        "thread_id": "t-phoenix",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Re: Contrato Projeto Phoenix",
        "body": "Já tiveste oportunidade de ver?",
    })

    log_event("Follow-up recebido", {
        "case": phoenix.title,
    })

    # --------------------------------------------------
    banner("PORTAIS APÓS ACTIVIDADE")

    attention_cards = attention_portal.collect(store, now)
    billing_cards = billing_portal.collect(store, now)
    classification_cards = classification_portal.collect(
        ingestion.pending_classifications, now
    )

    dashboard.render("attention", attention_cards)
    dashboard.render("billing", billing_cards)
    dashboard.render("classification", classification_cards)

    # --------------------------------------------------
    banner("DECISÃO DE BILLING")

    if billing_cards:
        billing_service.apply_decision(
            case_id=billing_cards[0].case_id,
            decision=BillingDecision.TO_BILL,
            context={"motivo": "Análise e negociação contratual"},
            now=now,
        )

        log_event("Billing decidido", {
            "case_id": billing_cards[0].case_id,
            "decisão": BillingDecision.TO_BILL.value,
        })
    else:
        log_event("Nenhum billing sugerido", {})

    # --------------------------------------------------
    banner("SILÊNCIO (10 DIAS)")

    now = now + timedelta(days=10)
    log_time(now)

    attention_cards = attention_portal.collect(store, now)
    dashboard.render("attention", attention_cards)

    # --------------------------------------------------
    banner("AUDITORIA FINAL")

    dump_store_verbose(store)
    assert_store_contract(store, clock)

    banner("FIM DO TESTE")


# ---------------------------------------------------------------------

if __name__ == "__main__":
    test_jornada_completa()


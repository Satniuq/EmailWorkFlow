"""
TESTE — DASHBOARD (ATTENTION CARDS)

Objectivo:
- forçar flags de atenção (STALE + OVERDUE)
- renderizar cartões no DashboardRenderer
- provar que o dashboard só mostra o que interessa agora
"""

from datetime import timedelta

from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from services.email_ingestion_service import EmailIngestionService
from dashboard.renderer import DashboardRenderer
from model.enums import CaseEventType, AttentionFlag


def banner(title):
    print("\n" + "=" * 90)
    print(title.center(90))
    print("=" * 90)


# “DecisionItem” minimalista: o renderer só precisa destes atributos
class SimpleDecision:
    def __init__(self, title, description, metadata=None):
        self.title = title
        self.description = description
        self.metadata = metadata or {}


def build_attention_decisions(case):
    decisions = []

    if AttentionFlag.OVERDUE in case.attention_flags:
        decisions.append(SimpleDecision(
            title="Atraso (OVERDUE)",
            description="O caso ultrapassou o prazo definido (due_at).",
            metadata={"case_id": case.id, "title": case.title, "due_at": case.due_at},
        ))

    if AttentionFlag.STALE in case.attention_flags:
        decisions.append(SimpleDecision(
            title="Estagnação (STALE)",
            description="O caso está sem actividade há mais de 7 dias.",
            metadata={"case_id": case.id, "title": case.title},
        ))

    return decisions


def test_dashboard_attention():
    banner("INICIALIZAÇÃO")

    clock = Clock()
    now = clock.now()

    store = InMemoryStore()
    brain = RulesEngine(store, CaseStateMachine())
    ingestion = EmailIngestionService(store, brain, clock)

    dashboard = DashboardRenderer()

    # --------------------------------------------------
    banner("CRIAR CASO (EMAIL INBOUND)")

    ingestion.ingest({
        "message_id": "att-001",
        "thread_id": "thread-att",
        "from": "cliente@empresa.com",
        "to": ["tu@escritorio.pt"],
        "subject": "Assunto com prazo",
        "body": "Precisamos disto resolvido.",
    })

    case = store.list_cases()[0]

    # Definir prazo no passado para forçar OVERDUE
    case.due_at = now - timedelta(days=1)

    # --------------------------------------------------
    banner("PASSAGEM DE TEMPO (8 DIAS) → FORÇAR STALE + OVERDUE")

    future = now + timedelta(days=8)

    # TIME_PASSED é contexto → força reavaliação de regras
    brain.handle_event(case, CaseEventType.TIME_PASSED, now=future)

    # --------------------------------------------------
    banner("DASHBOARD — ATTENTION")

    decisions = build_attention_decisions(case)
    dashboard.render("Attention", decisions)

    banner("FIM DO TESTE")


if __name__ == "__main__":
    test_dashboard_attention()

import os
from services.clock import Clock
from store.inmemory import InMemoryStore
from state_machine.case_state_machine import CaseStateMachine
from rules.rules_engine import RulesEngine
from services.email_ingestion_service import EmailIngestionService

from dashboard.renderer import DashboardRenderer
from model.enums import CaseEventType, AttentionFlag


# ---- decision item simples (igual ao teste) ----
class SimpleDecision:
    def __init__(self, title, description, metadata=None):
        self.title = title
        self.description = description
        self.metadata = metadata or {}


def build_attention_decisions(case):
    decisions = []

    if AttentionFlag.OVERDUE in case.attention_flags:
        decisions.append(SimpleDecision(
            "Atraso (OVERDUE)",
            "O caso ultrapassou o prazo definido.",
            {"case_id": case.id, "title": case.title, "due_at": case.due_at},
        ))

    if AttentionFlag.STALE in case.attention_flags:
        decisions.append(SimpleDecision(
            "Estagnação (STALE)",
            "O caso está sem actividade há mais de 7 dias.",
            {"case_id": case.id, "title": case.title},
        ))

    return decisions


class DashboardApp:
    def __init__(self):
        self.clock = Clock()
        self.store = InMemoryStore()
        self.state_machine = CaseStateMachine()
        self.rules = RulesEngine(self.store, self.state_machine)
        self.ingestion = EmailIngestionService(self.store, self.rules, self.clock)
        self.renderer = DashboardRenderer()

        self._bootstrap_data()

    def _bootstrap_data(self):
        # cria um caso real para veres algo
        self.ingestion.ingest({
            "message_id": "boot-001",
            "thread_id": "boot-thread",
            "from": "cliente@empresa.com",
            "to": ["tu@escritorio.pt"],
            "subject": "Assunto com prazo",
            "body": "Precisamos disto resolvido.",
        })

        case = self.store.list_cases()[0]
        case.due_at = self.clock.now() - timedelta(days=1)

        # força passagem de tempo
        future = self.clock.now() + timedelta(days=8)
        self.rules.handle_event(case, CaseEventType.TIME_PASSED, now=future)

    def run(self):
        while True:
            self._clear()

            case = self.store.list_cases()[0]
            decisions = build_attention_decisions(case)

            if decisions:
                self.renderer.render("Attention", decisions)
            else:
                print("\n✔️ Tudo em ordem. Nenhuma decisão necessária.\n")

            print("[1] resolver atraso   [2] marcar acompanhamento   [r] refrescar   [q] sair")
            choice = input("> ").strip().lower()

            if choice == "1":
                case = self.store.list_cases()[0]
                case.due_at = None

                # 🔑 força reavaliação das regras
                self.rules.handle_event(
                    case,
                    CaseEventType.USER_ACTION,
                    {"action": "resolve_overdue"},
                    now=self.clock.now(),
                )
                # resolveu o atraso
            
            elif choice == "2":
                case = self.store.list_cases()[0]

                # acção humana explícita → cria actividade
                self.rules.handle_event(
                    case,
                    CaseEventType.USER_ACTION,
                    {"action": "mark_followed_up"},
                    now=self.clock.now(),
                )


            elif choice == "q":
                break


    def _clear(self):
        os.system("cls" if os.name == "nt" else "clear")


if __name__ == "__main__":
    from datetime import timedelta
    DashboardApp().run()

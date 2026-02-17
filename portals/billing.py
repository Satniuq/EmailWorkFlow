"""
BillingPortal

Cria "cartas" que perguntam:
"Queres faturar isto?"

O portal não decide. Só detecta oportunidades de faturação.
"""

from datetime import datetime, timedelta
from typing import List

from model.enums import AttentionFlag
from model.entities import Case
from .base import DecisionPortal, DecisionItem


class BillingPortal(DecisionPortal):
    name = "billing"

    def __init__(self, window_days: int = 7):
        """
        window_days:
            Intervalo temporal que consideramos como "actividade recente".
            Mantém-se simples agora; depois pode ser configurável por cliente.
        """
        self.window_days = window_days

    def collect(self, store, now: datetime) -> List[DecisionItem]:
        decisions: List[DecisionItem] = []
        since = now - timedelta(days=self.window_days)

        for case in store.list_cases():
            # 1) Só faz sentido sugerir billing se o cérebro o marcou
            if AttentionFlag.BILLING_PENDING not in case.attention_flags:
                continue

            # 2) Criar um sumário claro do "porquê"
            activity = store.get_activity_summary(case.id, since)

            # Segurança: se por algum motivo não for significativo, não sugere
            if not activity.is_significant():
                continue

            decisions.append(self._make_decision(case, activity, since, now))

        return decisions

    def _make_decision(self, case: Case, activity, since: datetime, now: datetime) -> DecisionItem:
        """
        Constrói a carta de decisão de forma estável.
        A UI pode depois apresentar isto como swipe / botões / etc.
        """

        title = f"Faturação: {case.title}"

        desc_parts = []
        if activity.inbound_emails:
            desc_parts.append(f"{activity.inbound_emails} e-mail(s) recebidos")
        if activity.outbound_emails:
            desc_parts.append(f"{activity.outbound_emails} e-mail(s) enviados")
        if activity.tasks_completed:
            desc_parts.append(f"{activity.tasks_completed} tarefa(s) concluída(s)")
        if activity.notes:
            desc_parts.append(f"{activity.notes} nota(s)")

        description = (
            f"Actividade nos últimos {self.window_days} dias: "
            + ", ".join(desc_parts)
            + ".\n"
            + "Queres marcar isto como 'para faturar'?"
        )

        return DecisionItem(
            portal=self.name,
            case_id=case.id,
            client_id=case.client_id,
            title=title,
            description=description,
            metadata={
                "since": since.isoformat(),
                "now": now.isoformat(),
                "window_days": self.window_days,
                "activity": {
                    "inbound_emails": activity.inbound_emails,
                    "outbound_emails": activity.outbound_emails,
                    "notes": activity.notes,
                    "tasks_completed": activity.tasks_completed,
                },
            },
        )

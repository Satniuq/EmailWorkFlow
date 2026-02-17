"""
AttentionPortal

Portal que agrega Casos que pedem atenção imediata do utilizador.

Não pergunta "o que queres fazer?"
Pergunta:
- "onde é que o jogo está vivo?"
- "o que está a bloquear progresso?"
"""

from datetime import datetime
from typing import List

from model.enums import AttentionFlag, WorkStatus
from model.entities import Case
from .base import DecisionPortal, DecisionItem


class AttentionPortal(DecisionPortal):
    """
    Portal de atenção diária.

    Mostra Casos que:
    - estão atrasados
    - estão estagnados
    - têm sinais claros de fricção
    """

    name = "attention"

    def collect(self, store, now: datetime) -> List[DecisionItem]:
        decisions: List[DecisionItem] = []

        for case in store.list_cases():
            # 1️⃣ Casos arquivados não interessam
            if case.status == WorkStatus.ARCHIVED:
                continue

            # 2️⃣ Ver se há sinais de atenção relevantes
            flags = self._relevant_flags(case)
            if not flags:
                continue

            decisions.append(self._make_decision(case, flags, now))

        return decisions

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _relevant_flags(self, case: Case) -> List[AttentionFlag]:
        """
        Selecciona apenas os flags que justificam atenção activa.
        """

        relevant = []

        if AttentionFlag.OVERDUE in case.attention_flags:
            relevant.append(AttentionFlag.OVERDUE)

        if AttentionFlag.STALE in case.attention_flags:
            relevant.append(AttentionFlag.STALE)

        # UNREAD_MESSAGES pode ser afinado quando ligares email real
        if AttentionFlag.UNREAD_MESSAGES in case.attention_flags:
            relevant.append(AttentionFlag.UNREAD_MESSAGES)

        return relevant

    def _make_decision(
        self,
        case: Case,
        flags: List[AttentionFlag],
        now: datetime,
    ) -> DecisionItem:
        """
        Constrói a carta de atenção.
        """

        title = f"Atenção: {case.title}"

        reasons = []
        if AttentionFlag.OVERDUE in flags:
            reasons.append("prazo ultrapassado")
        if AttentionFlag.STALE in flags:
            reasons.append("sem actividade recente")
        if AttentionFlag.UNREAD_MESSAGES in flags:
            reasons.append("mensagens por ler")

        description = (
            "Este caso pede atenção porque tem "
            + ", ".join(reasons)
            + "."
        )

        return DecisionItem(
            portal=self.name,
            case_id=case.id,
            client_id=case.client_id,
            title=title,
            description=description,
            metadata={
                "flags": [f.value for f in flags],
                "status": case.status.value,
                "priority": case.priority.value,
                "generated_at": now.isoformat(),
            },
        )

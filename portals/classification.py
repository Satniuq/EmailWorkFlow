"""
ClassificationPortal

Portal de UI que apresenta ao utilizador decisões de classificação
que requerem confirmação humana.
"""

from datetime import datetime
from typing import List

from portals.base import DecisionPortal, DecisionItem
from portals.classification_decision import ClassificationDecision
from model.entities import Case


class ClassificationPortal(DecisionPortal):
    """
    Portal de confirmação de classificação.

    Mostra cartas do tipo:
    - "O sistema não tem a certeza. Confirma?"
    """

    name = "classification"

    def collect(
        self,
        pending_classifications: List[dict],
        now: datetime,
    ) -> List[DecisionItem]:
        """
        Recebe apenas decisões que requerem intervenção humana.
        """

        decisions: List[DecisionItem] = []

        for item in pending_classifications:
            email = item["email"]
            decision: ClassificationDecision = item["decision"]
            suggested_case: Case | None = item.get("suggested_case")

            decisions.append(
                self._make_decision(email, decision, suggested_case, now)
            )

        return decisions

    # ------------------------------------------------------------------

    def _make_decision(
        self,
        email,
        decision: ClassificationDecision,
        case: Case | None,
        now: datetime,
    ) -> DecisionItem:
        """
        Constrói a carta de decisão de classificação.
        """

        title = "Classificação de novo e-mail"

        case_title = case.title if case else "Novo caso"
        confidence_pct = int(decision.confidence * 100)

        description = (
            f"Recebi um novo e-mail com o assunto:\n"
            f"  “{email.subject}”\n\n"
            f"Classifiquei-o como pertencente ao caso:\n"
            f"  → {case_title}\n\n"
            f"Confiança: {confidence_pct}%\n"
            f"Motivo: {decision.reason}\n\n"
            f"O que queres fazer?"
        )

        return DecisionItem(
            portal=self.name,
            case_id=case.id if case else None,
            client_id=case.client_id if case else None,
            title=title,
            description=description,
            metadata={
                "message_id": email.message_id,
                "thread_id": email.thread_id,
                "suggested_case_id": case.id if case else None,
                "confidence": decision.confidence,
                "timestamp": now.isoformat(),
            },
        )

"""
ClassificationPortal

Portal que apresenta ao utilizador decisões de classificação
quando a confiança automática não é suficiente.

Este portal só aparece em casos de ambiguidade real.
"""

from datetime import datetime
from typing import List

from portals.base import DecisionPortal, DecisionItem
from services.classification_service import ClassificationResult
from model.entities import Case


class ClassificationPortal(DecisionPortal):
    """
    Portal de confirmação de classificação.

    Mostra cartas do tipo:
    - "Classifiquei este e-mail aqui, queres confirmar?"
    """

    name = "classification"

    def collect(
        self,
        pending_classifications: List[dict],
        now: datetime,
    ) -> List[DecisionItem]:
        """
        Recebe uma lista de classificações pendentes.

        Cada item em pending_classifications deve conter:
        - email (NormalizedEmail)
        - result (ClassificationResult)
        - suggested_case (Case | None)
        """

        decisions: List[DecisionItem] = []

        for item in pending_classifications:
            email = item["email"]
            result: ClassificationResult = item["result"]
            suggested_case: Case | None = item.get("suggested_case")

            # Só interessa quando o sistema pede ajuda
            if result.action != "ask_user":
                continue

            decisions.append(
                self._make_decision(email, result, suggested_case, now)
            )

        return decisions

    # ------------------------------------------------------------------

    def _make_decision(
        self,
        email,
        result: ClassificationResult,
        case: Case | None,
        now: datetime,
    ) -> DecisionItem:
        """
        Constrói a carta de decisão de classificação.
        """

        title = "Classificação de novo e-mail"

        case_title = case.title if case else "Novo caso"
        confidence_pct = int(result.confidence * 100)

        description = (
            f"Recebi um novo e-mail com o assunto:\n"
            f"  “{email.subject}”\n\n"
            f"Classifiquei-o como pertencente ao caso:\n"
            f"  → {case_title}\n\n"
            f"Confiança: {confidence_pct}%\n"
            f"Motivo: {result.rationale}\n\n"
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
                "confidence": result.confidence,
                "suggested_action": result.action,
                "timestamp": now.isoformat(),
            },
        )

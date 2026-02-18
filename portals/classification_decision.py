#portals/classification_decision.py

from dataclasses import dataclass
from typing import Optional, Literal

from services.classification_service import ClassificationResult

@dataclass
class ClassificationDecision:
    action: Literal["attach_existing", "create_new", "ask_user"]
    case_id: Optional[str]
    confidence: float
    reason: str


class ClassificationDecisionEngine:
    """
    Aplica política de decisão sobre resultados de classificação.
    """

    def decide(self, result: ClassificationResult) -> ClassificationDecision:
        if result.case_id is None:
            return ClassificationDecision(
                action="create_new",
                case_id=None,
                confidence=result.confidence,
                reason="Nenhum caso existente relevante.",
            )

        if result.confidence >= 0.8:
            return ClassificationDecision(
                action="attach_existing",
                case_id=result.case_id,
                confidence=result.confidence,
                reason="Confiança alta.",
            )

        if result.confidence >= 0.4:
            return ClassificationDecision(
                action="ask_user",
                case_id=result.case_id,
                confidence=result.confidence,
                reason="Confiança intermédia, requer confirmação humana.",
            )

        return ClassificationDecision(
            action="create_new",
            case_id=None,
            confidence=result.confidence,
            reason="Confiança baixa.",
        )

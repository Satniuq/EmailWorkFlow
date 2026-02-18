"""
ClassificationService

Responsável por decidir a que Caso um e-mail normalizado pertence,
ou se deve ser criado um novo Caso.

Este serviço:
- NÃO altera estados
- NÃO cria billing
- NÃO executa decisões humanas

Ele apenas classifica e devolve confiança.
"""

from dataclasses import dataclass
from typing import Optional, List
from difflib import SequenceMatcher

from model.entities import Case
from model.enums import WorkStatus
from services.email_normalizer import NormalizedEmail
from store.inmemory import InMemoryStore


@dataclass
class ClassificationResult:
    """
    Resultado de uma classificação de e-mail.
    """

    case_id: Optional[str]
    confidence: float
    rationale: str


class ClassificationService:
    """
    Serviço de classificação de e-mails.
    """

    def __init__(self, store: InMemoryStore):
        self.store = store

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def classify(self, email: NormalizedEmail) -> ClassificationResult:
        """
        Decide a que Caso um e-mail pertence.
        """

        candidates = self._candidate_cases(email)

        if not candidates:
            return ClassificationResult(
                case_id=None,
                confidence=0.9,
                rationale="Nenhum caso existente relevante encontrado.",
            )

        scored = [
            (case, self._score_case(case, email))
            for case in candidates
        ]

        scored.sort(key=lambda x: x[1], reverse=True)
        best_case, best_score = scored[0]



        return ClassificationResult(
            case_id=None,
            confidence=best_score,
            rationale="Correspondência fraca com casos existentes.",
        )

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------

    def _candidate_cases(self, email: NormalizedEmail) -> List[Case]:
        """
        Selecciona casos que podem ser relevantes para este e-mail.
        """

        cases = self.store.list_cases()

        # Ignorar casos arquivados
        cases = [c for c in cases if c.status != WorkStatus.ARCHIVED]

        # Contexto pessoal → não tenta colar a casos profissionais
        if email.context == "personal":
            return []

        return cases

    def _score_case(self, case: Case, email: NormalizedEmail) -> float:
        """
        Calcula um score [0.0 - 1.0] de correspondência entre email e caso.
        """

        score = 0.0

        # 1️⃣ Thread match (fortíssimo)
        if email.thread_id:
            for item in self.store.list_case_items(case.id):
                if item.metadata.get("thread_id") == email.thread_id:
                    score += 0.6
                    break

        # 2️⃣ Similaridade de assunto
        score += 0.2 * self._similarity(case.title.lower(), email.subject.lower())

        # 3️⃣ Contexto profissional
        if email.context == "professional":
            score += 0.2

        # Clamp
        return min(score, 1.0)

    @staticmethod
    def _similarity(a: str, b: str) -> float:
        """
        Similaridade simples entre strings.
        """
        return SequenceMatcher(None, a, b).ratio()

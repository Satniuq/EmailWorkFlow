"""
Email Normalizer

Responsável por converter um e-mail cru (IMAP / API)
num formato interno consistente e analisável.

Este módulo:
- NÃO cria Casos
- NÃO decide billing
- NÃO altera estados

Ele apenas extrai sinais.
"""

from dataclasses import dataclass
from typing import Optional
import re


@dataclass
class NormalizedEmail:
    """
    Representação interna e estável de um e-mail.
    """

    message_id: str
    thread_id: Optional[str]

    from_address: str
    to_addresses: list[str]

    subject: str
    body: str

    # Classificação heurística inicial
    context: str  # "professional" | "personal"
    confidence: float


class EmailNormalizer:
    """
    Normaliza e-mails e infere contexto inicial.
    """

    PROFESSIONAL_KEYWORDS = {
        "contrato",
        "proposta",
        "orçamento",
        "fatura",
        "invoice",
        "acordo",
        "pagamento",
        "projeto",
    }

    PERSONAL_KEYWORDS = {
        "jantar",
        "café",
        "almoço",
        "sexta",
        "sábado",
        "domingo",
    }

    def normalize(self, raw_email: dict) -> NormalizedEmail:
        """
        Recebe um e-mail cru (mock ou real) e devolve NormalizedEmail.
        """

        subject = (raw_email.get("subject") or "").lower()
        body = (raw_email.get("body") or "").lower()
        from_addr = raw_email.get("from", "")

        context, confidence = self._infer_context(subject, body, from_addr)

        return NormalizedEmail(
            message_id=raw_email["message_id"],
            thread_id=raw_email.get("thread_id"),
            from_address=from_addr,
            to_addresses=raw_email.get("to", []),
            subject=raw_email.get("subject", ""),
            body=raw_email.get("body", ""),
            context=context,
            confidence=confidence,
        )

    # ------------------------------------------------------------------

    def _infer_context(self, subject: str, body: str, from_addr: str) -> tuple[str, float]:
        """
        Inferência heurística simples (mas extensível).
        """

        score = 0.0

        # Palavras-chave profissionais
        for kw in self.PROFESSIONAL_KEYWORDS:
            if kw in subject or kw in body:
                score += 0.3

        # Palavras-chave pessoais
        for kw in self.PERSONAL_KEYWORDS:
            if kw in subject or kw in body:
                score -= 0.2

        # Domínio de email
        if re.search(r"@(gmail|hotmail|outlook)\.", from_addr):
            score -= 0.1
        else:
            score += 0.2

        # Clamp simples
        score = max(min(score, 1.0), -1.0)

        if score >= 0.3:
            return "professional", score
        elif score <= -0.3:
            return "personal", abs(score)
        else:
            return "ambiguous", abs(score)

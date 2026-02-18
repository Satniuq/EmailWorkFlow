"""
Catálogo canónico de eventos do sistema.

Este módulo define:
- o significado semântico de cada evento
- o que um evento representa no mundo real
- que efeitos EXPECTÁVEIS pode ter (não executados aqui)

NÃO contém:
- lógica
- regras
- efeitos colaterais
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Set


class EventSemantic(Enum):
    """
    Semântica abstracta de um evento.
    Um evento pode ter várias.
    """

    ACTIVITY = auto()
    """
    Cria actividade no Caso.
    Quebra estagnação (STALE).
    """

    FOLLOW_UP = auto()
    """
    Representa acompanhamento activo do utilizador.
    """

    RESOLVE_OVERDUE = auto()
    """
    Resolve atraso tácito (ex: resposta enviada).
    """

    DECISION = auto()
    """
    Decisão humana consciente.
    """

    TIME_CONTEXT = auto()
    """
    Passagem de tempo sem actividade.
    """

    SYSTEM = auto()
    """
    Acção automática do sistema.
    """

    BILLING_DECISION = auto()
    """
    Decisão humana de faturação.
    """



@dataclass(frozen=True)
class CaseEventSpec:
    """
    Especificação semântica de um evento.
    """

    name: str
    semantics: Set[EventSemantic]
    description: str


# ------------------------------------------------------------------
# CATÁLOGO DE EVENTOS DO SISTEMA
# ------------------------------------------------------------------

CASE_EVENTS: dict[str, CaseEventSpec] = {

    # --------------------------------------------------
    # EMAILS
    # --------------------------------------------------

    "EMAIL_INBOUND": CaseEventSpec(
        name="EMAIL_INBOUND",
        semantics={
            EventSemantic.ACTIVITY,
        },
        description=(
            "Email recebido do exterior. "
            "Introduz nova informação e pode reactivar o Caso."
        ),
    ),

    "EMAIL_OUTBOUND": CaseEventSpec(
        name="EMAIL_OUTBOUND",
        semantics={
            EventSemantic.ACTIVITY,
            EventSemantic.FOLLOW_UP,
            EventSemantic.RESOLVE_OVERDUE,
        },
        description=(
            "Email enviado pelo utilizador. "
            "Conta como acompanhamento activo e resolve atrasos tácitos."
        ),
    ),

    # --------------------------------------------------
    # ACÇÕES HUMANAS
    # --------------------------------------------------

    "USER_ACTION": CaseEventSpec(
        name="USER_ACTION",
        semantics={
            EventSemantic.ACTIVITY,
            EventSemantic.DECISION,
            EventSemantic.BILLING_DECISION,
        },
        description=(
            "Acção humana explícita no sistema "
            "(nota, decisão, marcação manual)."
        ),
    ),

    # --------------------------------------------------
    # TEMPO
    # --------------------------------------------------

    "TIME_PASSED": CaseEventSpec(
        name="TIME_PASSED",
        semantics={
            EventSemantic.TIME_CONTEXT,
        },
        description=(
            "Passagem de tempo sem actividade. "
            "Nunca cria actividade nem resolve problemas."
        ),
    ),

    # --------------------------------------------------
    # SISTEMA
    # --------------------------------------------------

    "SYSTEM_ACTION": CaseEventSpec(
        name="SYSTEM_ACTION",
        semantics={
            EventSemantic.SYSTEM,
        },
        description=(
            "Acção automática do sistema "
            "(arquivo, manutenção, limpeza)."
        ),
    ),
}

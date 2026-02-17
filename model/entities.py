from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any, List

from .enums import (
    WorkStatus,
    Priority,
    CaseItemKind,
    BillingDecision,
    AttentionFlag,
)


@dataclass
class Case:
    """
    Representa uma unidade contínua de relação profissional.
    Não é um 'assunto fechado', mas um fluxo de trabalho.
    """

    id: str
    title: str
    client_id: str

    status: WorkStatus
    priority: Priority

    created_at: datetime
    updated_at: datetime

    due_at: Optional[datetime] = None

    # Flags derivados (não são decisões)
    attention_flags: set[AttentionFlag] = field(default_factory=set)

@dataclass
class CaseItem:
    """
    Um evento ou artefacto associado a um Caso.
    Tudo o que acontece ao Caso passa por aqui.
    """

    id: str
    case_id: str
    kind: CaseItemKind

    created_at: datetime

    ref_id: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class BillingRecord:
    """
    Registo de uma decisão de faturação.
    Não é uma factura.
    """

    id: str
    case_id: str
    client_id: str

    decision: BillingDecision
    decided_at: datetime

    context: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ActivitySummary:
    """
    Agregado de actividade recente de um Caso.
    Usado por Portais de decisão.
    """

    case_id: str
    since: datetime

    inbound_emails: int = 0
    outbound_emails: int = 0
    notes: int = 0
    tasks_completed: int = 0

    def is_significant(self) -> bool:
        """
        Heurística mínima para decidir se merece atenção.
        """
        return (
            self.inbound_emails > 0
            or self.outbound_emails > 0
            or self.tasks_completed > 0
        )

"""
InMemoryStore

Implementação em memória do repositório de dados do sistema.
Serve para:
- desenvolvimento
- testes
- simulações
- clarificar a API antes de uma BD real

Regra de ouro:
Este módulo NÃO contém lógica de negócio.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4
from services.clock import Clock


from model.entities import (
    Case,
    CaseItem,
    BillingRecord,
    ActivitySummary,
)
from model.enums import (
    CaseItemKind,
    BillingDecision,
    AttentionFlag,
)


class InMemoryStore:
    """
    Store central do sistema.

    Guarda tudo em estruturas simples de memória.
    Todos os outros módulos dependem desta API,
    NÃO da forma como os dados são guardados.
    """

    def __init__(self):
        # Casos por ID
        self._cases: Dict[str, Case] = {}

        # Itens de caso (linha do tempo)
        self._case_items: List[CaseItem] = []

        # Registos de billing
        self._billing_records: List[BillingRecord] = []

    # ------------------------------------------------------------------
    # CASES
    # ------------------------------------------------------------------

    def add_case(self, case: Case) -> None:
        """
        Regista um novo Caso.
        """
        self._cases[case.id] = case

    def get_case(self, case_id: str) -> Optional[Case]:
        """
        Obtém um Caso por ID.
        """
        return self._cases.get(case_id)

    def list_cases(self) -> List[Case]:
        """
        Lista todos os Casos.
        O filtro (ativos, arquivados, etc.) é feito fora.
        """
        return list(self._cases.values())

    # ------------------------------------------------------------------
    # CASE ITEMS (eventos, emails, notas, billing, etc.)
    # ------------------------------------------------------------------

    def add_case_item(
        self,
        case_id: str,
        kind: CaseItemKind,
        ref_id: Optional[str] = None,
        metadata: Optional[dict] = None,
        created_at: Optional[datetime] = None,
    ) -> CaseItem:

        """
        Regista um item associado a um Caso.
        Usado por emails, notas, tarefas, billing, etc.
        """

        item = CaseItem(
            id=str(uuid4()),
            case_id=case_id,
            kind=kind,
            created_at=created_at or Clock().now(),
            ref_id=ref_id,
            metadata=metadata or {},
        )


        self._case_items.append(item)
        return item

    def list_case_items(self, case_id: str) -> List[CaseItem]:
        """
        Devolve a linha temporal completa de um Caso.
        """
        return [i for i in self._case_items if i.case_id == case_id]

    # ------------------------------------------------------------------
    # BILLING
    # ------------------------------------------------------------------

    def add_billing_record(
        self,
        case: Case,
        decision: BillingDecision,
        context: Optional[dict] = None,
    ) -> BillingRecord:
        """
        Regista uma decisão de faturação.
        """

        record = BillingRecord(
            id=str(uuid4()),
            case_id=case.id,
            client_id=case.client_id,
            decision=decision,
            decided_at=datetime.utcnow(),
            context=context or {},
        )

        self._billing_records.append(record)

        # Marcar que já não está pendente
        case.attention_flags.discard(AttentionFlag.BILLING_PENDING)

        return record

    def list_billing_records(self, case_id: Optional[str] = None) -> List[BillingRecord]:
        """
        Lista registos de billing.
        Pode filtrar por Caso.
        """
        if case_id:
            return [b for b in self._billing_records if b.case_id == case_id]
        return list(self._billing_records)

    # ------------------------------------------------------------------
    # ACTIVITY / AGREGADOS
    # ------------------------------------------------------------------

    def get_activity_summary(
        self,
        case_id: str,
        since: datetime,
    ) -> ActivitySummary:
        """
        Cria um agregado de actividade recente para um Caso.
        Usado por Decision Portals.
        """

        summary = ActivitySummary(case_id=case_id, since=since)

        for item in self.list_case_items(case_id):
            if item.created_at < since:
                continue

            if item.kind == CaseItemKind.EMAIL:
                direction = item.metadata.get("direction")
                if direction == "inbound":
                    summary.inbound_emails += 1
                elif direction == "outbound":
                    summary.outbound_emails += 1

            elif item.kind == CaseItemKind.NOTE:
                summary.notes += 1

            elif item.kind == CaseItemKind.TASK:
                if item.metadata.get("completed"):
                    summary.tasks_completed += 1

        return summary

    # ------------------------------------------------------------------
    # ATTENTION FLAGS (derivados, nunca manuais)
    # ------------------------------------------------------------------

    def mark_overdue(self, case: Case) -> None:
        """
        Marca um Caso como atrasado.
        Chamado pelo Rules Engine.
        """
        case.attention_flags.add(AttentionFlag.OVERDUE)

    def mark_billing_pending(self, case: Case) -> None:
        """
        Indica que há actividade relevante que pode gerar faturação.
        """
        case.attention_flags.add(AttentionFlag.BILLING_PENDING)

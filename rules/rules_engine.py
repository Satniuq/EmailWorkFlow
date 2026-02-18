"""
Rules Engine

Este módulo contém regras automáticas do sistema.
As regras:
- reagem a eventos
- analisam passagem do tempo
- marcam atenção
- sugerem decisões (ex: billing)

NUNCA:
- alteram estados directamente
- executam decisões humanas
"""

from datetime import datetime, timedelta

from model.enums import (
    CaseEventType,
    AttentionFlag,
    CaseItemKind,
    Priority,
    BillingDecision
)
from model.entities import Case, BillingRecord
from model.events import CASE_EVENTS, EventSemantic
from state_machine.case_state_machine import CaseStateMachine
from store.protocol import StoreProtocol
from services.clock import Clock
from uuid import uuid4

FOLLOW_UP_DAYS = 7


class RulesEngine:
    """
    Cérebro automático do sistema.

    Recebe eventos e:
    - regista actividade factual
    - dispara a State Machine
    - aplica semântica do evento
    - calcula atenção e billing
    """

    def __init__(self, store: StoreProtocol, state_machine: CaseStateMachine):
        self.store = store
        self.state_machine = state_machine

    # ------------------------------------------------------------------
    # API PÚBLICA
    # ------------------------------------------------------------------

    def handle_event(
        self,
        case: Case,
        event_type: CaseEventType,
        event_context: dict | None = None,
        now: datetime | None = None,
    ) -> None:
        """
        Ponto único de entrada para eventos no sistema.
        Aplica o pipeline completo e explícito.
        """

        now = now or Clock().now()
        event_context = event_context or {}

        # 1️⃣ Registo factual (factos, não decisões)
        self._phase_record_facts(case, event_type, event_context, now)

        # 2️⃣ Transição de estado (State Machine)
        self._phase_state_transition(case, event_type)

        # 3️⃣ Semântica do evento (efeitos imediatos)
        self._phase_event_semantics(case, event_type, event_context, now)

        # 4️⃣ Regras de atenção (derivadas, nunca decisivas)
        self._phase_attention(case, now)

        # 5️⃣ Regras de billing (sugestão, não decisão)
        self._phase_billing(case, event_type, now)

        # 6️⃣ Actualização temporal do Caso
        if event_type != CaseEventType.TIME_PASSED:
            case.updated_at = now


    # ------------------------------------------------------------------
    # MÉTODOS PRIVADOS
    # ------------------------------------------------------------------

    def _phase_record_facts(
        self,
        case: Case,
        event_type: CaseEventType,
        context: dict,
        now: datetime,
    ) -> None:
        self._record_case_item(case, event_type, context, now)


    def _phase_state_transition(
        self,
        case: Case,
        event_type: CaseEventType,
    ) -> None:
        self.state_machine.apply(case, event_type)


    def _phase_event_semantics(
        self,
        case: Case,
        event_type: CaseEventType,
        context: dict,
        now: datetime,
    ) -> None:
        self._apply_event_semantics(case, event_type, context, now)


    def _phase_attention(
        self,
        case: Case,
        now: datetime,
    ) -> None:
        self._apply_attention_rules(case, now)


    def _phase_billing(
        self,
        case: Case,
        event_type: CaseEventType,
        now: datetime,
    ) -> None:
        spec = CASE_EVENTS[event_type.name]
        if EventSemantic.BILLING_DECISION in spec.semantics:
            return

        self._apply_billing_rules(case, now)


    # ------------------------------------------------------------------
    # SEMÂNTICA DOS EVENTOS
    # ------------------------------------------------------------------

    def _schedule_follow_up(self, case: Case, now: datetime) -> None:
        """
        Cria um novo lembrete implícito de acompanhamento.
        Só se ainda não existir um due_at futuro.
        """

        if case.due_at and case.due_at > now:
            # já existe follow-up agendado
            return

        case.due_at = now + timedelta(days=FOLLOW_UP_DAYS)


    def _apply_event_semantics(
        self,
        case: Case,
        event_type: CaseEventType,
        event_context: dict,
        now: datetime,
    ) -> None:
        """
        Aplica efeitos semânticos do evento.
        """

        spec = CASE_EVENTS[event_type.name]

        if EventSemantic.RESOLVE_OVERDUE in spec.semantics:
            self._resolve_overdue(case, now)

        if EventSemantic.FOLLOW_UP in spec.semantics:
            self._schedule_follow_up(case, now)

        if EventSemantic.BILLING_DECISION in spec.semantics:
            self._apply_billing_decision(case, event_context, now)



    def _resolve_overdue(self, case: Case, now: datetime) -> None:
        """
        Resolver atraso de forma tácita (ex: email enviado).
        """

        if case.due_at and now >= case.due_at:
            case.due_at = None

    # ------------------------------------------------------------------
    # REGISTO FACTUAL
    # ------------------------------------------------------------------

    def _record_case_item(
        self,
        case: Case,
        event_type: CaseEventType,
        context: dict,
        now: datetime,
    ) -> None:
        """
        Converte eventos abstractos em CaseItems concretos.
        """

        if event_type in (
            CaseEventType.EMAIL_INBOUND,
            CaseEventType.EMAIL_OUTBOUND,
        ):
            self.store.add_case_item(
                case_id=case.id,
                kind=CaseItemKind.EMAIL,
                created_at=now,
                metadata={
                    "direction": "inbound"
                    if event_type == CaseEventType.EMAIL_INBOUND
                    else "outbound",
                    **context,
                },
            )

        elif event_type == CaseEventType.USER_ACTION:
            self.store.add_case_item(
                case_id=case.id,
                kind=CaseItemKind.NOTE,
                created_at=now,
                metadata=context,
            )

        elif event_type == CaseEventType.SYSTEM_ACTION:
            self.store.add_case_item(
                case_id=case.id,
                kind=CaseItemKind.NOTE,
                created_at=now,
                metadata={"system": True, **context},
            )

        # TIME_PASSED não cria item

    # ------------------------------------------------------------------
    # REGRAS DE ATENÇÃO
    # ------------------------------------------------------------------

    def _apply_attention_rules(self, case: Case, now: datetime) -> None:
        """
        Determina se algo merece atenção do utilizador.
        """

        # --- Atraso ---
        if case.due_at and now > case.due_at:
            case.attention_flags.add(AttentionFlag.OVERDUE)
        else:
            case.attention_flags.discard(AttentionFlag.OVERDUE)

        # --- Estagnação ---
        last_activity = self._last_activity_at(case)
        if last_activity:
            if last_activity.tzinfo is None:
                last_activity = last_activity.replace(tzinfo=now.tzinfo)

            if (now - last_activity) > timedelta(days=7):
                case.attention_flags.add(AttentionFlag.STALE)
            else:
                case.attention_flags.discard(AttentionFlag.STALE)

    # ------------------------------------------------------------------
    # REGRAS DE BILLING
    # ------------------------------------------------------------------

    def _apply_billing_decision(
        self,
        case: Case,
        context: dict,
        now: datetime,
    ) -> None:
        """
        Regista uma decisão de faturação e fecha o ciclo.
        """

        decision = context.get("decision")
        if not isinstance(decision, BillingDecision):
            return  # defensivo

        record = BillingRecord(
            id=str(uuid4()),
            case_id=case.id,
            client_id=case.client_id,
            decision=decision,
            decided_at=now,
            context=context,
        )

        self.store.add_billing_record(record)

        # fechar sugestão
        case.attention_flags.discard(AttentionFlag.BILLING_PENDING)


    def _apply_billing_rules(self, case: Case, now: datetime) -> None:
        """
        Decide se há actividade que justifica sugerir faturação.
        """

        if not self._is_billable_case(case):
            case.attention_flags.discard(AttentionFlag.BILLING_PENDING)
            return

        since = now - timedelta(days=7)
        activity = self.store.get_activity_summary(case.id, since)

        if activity.is_significant():
            case.attention_flags.add(AttentionFlag.BILLING_PENDING)
        else:
            case.attention_flags.discard(AttentionFlag.BILLING_PENDING)

    # ------------------------------------------------------------------
    # UTILITÁRIOS
    # ------------------------------------------------------------------

    def _is_billable_case(self, case: Case) -> bool:
        """
        Determina se um Caso é elegível para faturação.
        """

        if case.priority == Priority.LOW:
            return False

        billing_records = self.store.list_billing_records(case.id)
        if billing_records:
            return True

        return case.priority in {
            Priority.NORMAL,
            Priority.HIGH,
            Priority.URGENT,
        }

    def _last_activity_at(self, case: Case) -> datetime | None:
        """
        Última actividade registada num Caso.
        """

        items = self.store.list_case_items(case.id)
        if not items:
            return None

        return max(item.created_at for item in items)

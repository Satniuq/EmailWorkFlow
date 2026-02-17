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
)
from model.entities import Case
from state_machine.case_state_machine import CaseStateMachine
from store.protocol import StoreProtocol
from services.clock import Clock


class RulesEngine:
    """
    Cérebro automático do sistema.

    Recebe eventos e:
    - dispara a State Machine
    - marca flags de atenção
    - regista actividade
    """
    def __init__(self, store: StoreProtocol, state_machine: CaseStateMachine):
        self.store = store
        self.state_machine = state_machine


    # ------------------------------------------------------------------
    # EVENTOS
    # ------------------------------------------------------------------

    def _is_billable_case(self, case: Case) -> bool:
        """
        Determina se um Caso é elegível para faturação.
        """

        # Casos pessoais nunca são faturáveis
        if case.priority == Priority.LOW:
            return False

        # Se já houve billing antes, é faturável
        billing_records = self.store.list_billing_records(case.id)
        if billing_records:
            return True

        # Casos normais ou urgentes são faturáveis por defeito
        return case.priority in {Priority.NORMAL, Priority.HIGH, Priority.URGENT}


    def handle_event(
        self,
        case: Case,
        event_type: CaseEventType,
        event_context: dict | None = None,
        now: datetime | None = None,
    ) -> None:
        """
        Ponto único de entrada para eventos no sistema.

        Qualquer coisa que 'aconteça' passa por aqui:
        - emails
        - ações do utilizador
        - manutenção
        """

        now = now or Clock().now()
        event_context = event_context or {}

        # 1️⃣ Registar actividade factual
        self._record_case_item(case, event_type, event_context, now)

        # 2️⃣ Aplicar transição de estado (se existir)
        self.state_machine.apply(case, event_type)

        # 3️⃣ Aplicar regras derivadas
        self._apply_attention_rules(case, now)
        self._apply_billing_rules(case, now)

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
                metadata=context,
            )

        elif event_type == CaseEventType.SYSTEM_ACTION:
            self.store.add_case_item(
                case_id=case.id,
                kind=CaseItemKind.NOTE,
                metadata={"system": True, **context},
            )

        # TIME_PASSED não cria item: é contexto, não acontecimento

    # ------------------------------------------------------------------
    # REGRAS DE ATENÇÃO
    # ------------------------------------------------------------------

    def _apply_attention_rules(self, case: Case, now: datetime) -> None:
        """
        Regras que determinam se algo merece atenção do utilizador.
        """

        # --- Atraso ---
        if case.due_at and now > case.due_at:
            case.attention_flags.add(AttentionFlag.OVERDUE)
        else:
            case.attention_flags.discard(AttentionFlag.OVERDUE)

        # --- Mensagens não lidas (placeholder) ---
        # Isto será refinado quando ligares email real
        # Por agora, o simples facto de inbound recente já é sinal

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

    def _apply_billing_rules(self, case: Case, now: datetime) -> None:
        """
        Decide se há actividade que justifica sugerir faturação.
        """

        # ❗ REGRA-CHAVE: só casos profissionais entram em billing
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

    def _last_activity_at(self, case: Case) -> datetime | None:
        """
        Determina a última actividade registada num Caso.
        """

        items = self.store.list_case_items(case.id)
        if not items:
            return None

        return max(item.created_at for item in items)

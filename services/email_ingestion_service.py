"""
EmailIngestionService

Orquestrador do fluxo de entrada de e-mails no sistema.

Responsabilidades:
- normalizar e-mails
- avaliar e-mails automaticamente
- criar / associar Casos
- garantir continuidade quando plausível
- disparar eventos no RulesEngine
- guardar classificações pendentes quando há ambiguidade
"""

from datetime import datetime
from typing import List, Dict, Optional
from uuid import uuid4
from store.protocol import StoreProtocol

from services.email_normalizer import EmailNormalizer, NormalizedEmail
from services.classification_service import ClassificationService
from portals.classification_decision import (
    ClassificationDecisionEngine,
    ClassificationDecision,
)
from rules.rules_engine import RulesEngine
from model.entities import Case
from model.enums import (
    WorkStatus,
    Priority,
    CaseEventType,
)


class EmailIngestionService:
    """
    Ponto único de entrada de e-mails no sistema.
    """

    def __init__(
        self,
        store: StoreProtocol,
        rules_engine: RulesEngine,
        clock,
    ):
        self.store = store
        self.rules_engine = rules_engine
        self.clock = clock

        self.normalizer = EmailNormalizer()
        self.classifier = ClassificationService(store)
        self.classification_decider = ClassificationDecisionEngine()

        # Pendências para o ClassificationPortal
        self.pending_classifications: List[Dict] = []

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def ingest(self, raw_email: dict) -> None:
        now = self.clock.now()

        # 1️⃣ Normalizar
        email = self.normalizer.normalize(raw_email)

        # 2️⃣ CONTINUIDADE TEM PRIORIDADE ABSOLUTA
        continuation = self._find_continuation_case(email, now)
        if continuation:
            print("🧠 CONTINUIDADE APLICADA")
            print(f"   • case_id: {continuation.id}")
            print(f"   • motivo: thread_id ou heurística")

            self._attach_to_case_by_id(email, continuation.id, now)
            return

        print("🧠 SEM CONTINUIDADE — A CLASSIFICAR")

        # 3️⃣ Casos pessoais não entram no fluxo
        if email.context == "personal":
            self._create_personal_case(email)
            return

        # 4️⃣ Avaliar (factos)
        result = self.classifier.classify(email)

        # 5️⃣ Decidir (política)
        decision = self.classification_decider.decide(result)

        # 6️⃣ Executar decisão
        if decision.action == "attach_existing":
            self._attach_to_case_by_id(email, decision.case_id, now)

        elif decision.action == "create_new":
            self._create_new_case(email, decision, now)

        elif decision.action == "ask_user":
            self._enqueue_pending(email, decision, now)

        else:
            raise RuntimeError(f"Decisão desconhecida: {decision.action}")


    # ------------------------------------------------------------------
    # Caminhos
    # ------------------------------------------------------------------

    def _create_personal_case(self, email: NormalizedEmail) -> None:
        """
        Cria um Caso pessoal fora do fluxo económico.
        """

        now = self.clock.now()

        case = Case(
            id=str(uuid4()),
            title=email.subject or "Assunto pessoal",
            client_id=email.from_address,
            status=WorkStatus.NEW,
            priority=Priority.LOW,   # 🔒 nunca faturável
            created_at=now,
            updated_at=now,
            due_at=None,
        )

        self.store.add_case(case)

        # ❗ NOTA: casos pessoais não disparam rules_engine

    def _attach_to_case_by_id(
        self,
        email: NormalizedEmail,
        case_id: str,
        now: datetime,
    ) -> None:
        case = self.store.get_case(case_id)
        if not case:
            return

        self.rules_engine.handle_event(
            case=case,
            event_type=CaseEventType.EMAIL_INBOUND,
            event_context={
                "message_id": email.message_id,
                "thread_id": email.thread_id,
                "from": email.from_address,
                "subject": email.subject,
            },
            now=now,
        )

    def _create_new_case(
        self,
        email: NormalizedEmail,
        decision: ClassificationDecision,
        now: datetime,
    ) -> None:
        """
        Cria um novo Caso a partir de um e-mail.
        """

        case = Case(
            id=str(uuid4()),
            title=email.subject or "Novo assunto",
            client_id=email.from_address,
            status=WorkStatus.NEW,
            priority=self._infer_priority(email),
            created_at=now,
            updated_at=now,
            due_at=None,
        )

        self.store.add_case(case)

        self.rules_engine.handle_event(
            case=case,
            event_type=CaseEventType.EMAIL_INBOUND,
            event_context={
                "message_id": email.message_id,
                "thread_id": email.thread_id,
                "from": email.from_address,
                "subject": email.subject,
                "confidence": decision.confidence,
            },
            now=now,
        )

    def _enqueue_pending(
        self,
        email: NormalizedEmail,
        decision: ClassificationDecision,
        now: datetime,
    ) -> None:
        suggested_case = (
            self.store.get_case(decision.case_id)
            if decision.case_id
            else None
        )

        self.pending_classifications.append(
            {
                "email": email,
                "decision": decision,
                "suggested_case": suggested_case,
                "created_at": now,
            }
        )

    # ------------------------------------------------------------------
    # Heurísticas locais
    # ------------------------------------------------------------------

    def _infer_priority(self, email: NormalizedEmail) -> Priority:
        """
        Infer prioridade inicial de um novo Caso.
        """

        if email.context == "professional":
            return Priority.NORMAL

        return Priority.LOW

    def _find_continuation_case(
        self,
        email: NormalizedEmail,
        now: datetime,
    ) -> Optional[Case]:
        """
        Tenta encontrar um Caso existente plausível para continuação.
        Heurística conservadora e explicável.
        """

        # 1️⃣ thread_id é critério forte
        if email.thread_id:
            for case in self.store.list_cases():
                for item in self.store.list_case_items(case.id):
                    if item.metadata.get("thread_id") == email.thread_id:
                        return case

        # 2️⃣ Mesmo remetente + mesmo assunto + recente
        for case in self.store.list_cases():
            if case.client_id != email.from_address:
                continue

            if case.title.strip().lower() != (email.subject or "").strip().lower():
                continue

            if (now - case.created_at).days <= 7:
                return case

        return None

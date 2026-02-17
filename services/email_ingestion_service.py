"""
EmailIngestionService

Orquestrador do fluxo de entrada de e-mails no sistema.

Responsabilidades:
- normalizar e-mails
- classificar automaticamente
- criar / associar Casos
- garantir continuidade quando plausível
- disparar eventos no RulesEngine
- guardar classificações pendentes quando há ambiguidade
"""

from datetime import datetime
from typing import List, Dict, Optional
from uuid import uuid4

from services.email_normalizer import EmailNormalizer, NormalizedEmail
from services.classification_service import ClassificationService, ClassificationResult
from rules.rules_engine import RulesEngine
from store.inmemory import InMemoryStore
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
        store: InMemoryStore,
        rules_engine: RulesEngine,
        clock,
    ):
        self.store = store
        self.rules_engine = rules_engine
        self.clock = clock

        self.normalizer = EmailNormalizer()
        self.classifier = ClassificationService(store)

        # Pendências para o ClassificationPortal
        self.pending_classifications: List[Dict] = []

    # ------------------------------------------------------------------
    # API pública
    # ------------------------------------------------------------------

    def ingest(self, raw_email: dict) -> None:
        """
        Ingestão completa de um e-mail cru.
        """

        now = self.clock.now()

        # 1️⃣ Normalizar
        email = self.normalizer.normalize(raw_email)

        # 2️⃣ CONTINUIDADE TEM PRIORIDADE ABSOLUTA
        continuation = self._find_continuation_case(email, now)
        if continuation:
            print("🧠 CONTINUIDADE APLICADA")
            print(f"   • case_id: {continuation.id}")
            print(f"   • motivo: thread_id ou heurística")
            synthetic_result = ClassificationResult(
                action="attach_existing",
                case_id=continuation.id,
                confidence=0.6,
                rationale="Continuidade por thread_id ou heurística recente.",
            )
            self._attach_to_case(email, synthetic_result, now)
            return

        print("🧠 SEM CONTINUIDADE — A CLASSIFICAR")

        # 3️⃣ Se NÃO há continuidade, aplicar regras de contexto
        if email.context == "personal":
            self._create_personal_case(email)
            return

        # 4️⃣ Classificar
        result = self.classifier.classify(email)

        # 5️⃣ Decidir caminho
        if result.action == "attach_existing":
            self._attach_to_case(email, result, now)

        elif result.action == "create_new":
            self._create_new_case(email, result, now)

        elif result.action == "ask_user":
            self._enqueue_pending(email, result, now)

        else:
            raise RuntimeError(f"Ação de classificação desconhecida: {result.action}")

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

    def _attach_to_case(
        self,
        email: NormalizedEmail,
        result: ClassificationResult,
        now: datetime,
    ) -> None:
        """
        Anexa e-mail a um Caso existente e dispara evento.
        """

        case = self.store.get_case(result.case_id)
        if not case:
            # fallback defensivo
            self._create_new_case(email, result, now)
            return

        self.rules_engine.handle_event(
            case=case,
            event_type=CaseEventType.EMAIL_INBOUND,
            event_context={
                "message_id": email.message_id,
                "thread_id": email.thread_id,
                "from": email.from_address,
                "subject": email.subject,
                "confidence": result.confidence,
            },
            now=now,
        )

    def _create_new_case(
        self,
        email: NormalizedEmail,
        result: ClassificationResult,
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
                "confidence": result.confidence,
            },
            now=now,
        )

    def _enqueue_pending(
        self,
        email: NormalizedEmail,
        result: ClassificationResult,
        now: datetime,
    ) -> None:
        """
        Guarda classificação pendente para decisão humana.
        """

        suggested_case = (
            self.store.get_case(result.case_id)
            if result.case_id
            else None
        )

        self.pending_classifications.append(
            {
                "email": email,
                "result": result,
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

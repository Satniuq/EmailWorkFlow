from enum import Enum, auto

class WorkStatus(Enum):
    """
    Estado lógico de um Caso no ciclo de trabalho.
    Não representa urgência nem faturação.
    """

    NEW = "new"
    IN_PROGRESS = "in_progress"
    WAITING_REPLY = "waiting_reply"
    DONE = "done"
    ARCHIVED = "archived"


class Priority(Enum):
    """
    Importância intrínseca do caso.
    Não depende de prazos.
    """

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class CaseEventType(Enum):
    """
    Eventos abstractos que podem afectar um Caso.
    São usados pela State Machine e Rules Engine.
    """

    EMAIL_INBOUND = auto()
    EMAIL_OUTBOUND = auto()
    TIME_PASSED = auto()
    USER_ACTION = auto()
    SYSTEM_ACTION = auto()

class CaseItemKind(Enum):
    """
    Tipos de itens associados a um Caso.
    Um Caso é uma sequência destes itens.
    """

    EMAIL = "email"
    NOTE = "note"
    TASK = "task"
    DOCUMENT = "document"
    BILLING_EVENT = "billing_event"

class BillingDecision(Enum):
    """
    Decisão consciente do utilizador relativamente a faturação.
    """

    TO_BILL = "to_bill"
    DONT_BILL = "dont_bill"
    DEFER = "defer"

class AttentionFlag(Enum):
    """
    Marcadores que indicam que algo merece atenção.
    Não alteram o estado do Caso.
    """

    OVERDUE = "overdue"
    UNREAD_MESSAGES = "unread_messages"
    BILLING_PENDING = "billing_pending"
    STALE = "stale"

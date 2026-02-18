from datetime import timedelta
from uuid import uuid4

from model.enums import CaseEventType
from services.email_normalizer import NormalizedEmail


class EmailSimulator:
    """
    Simula o mundo exterior:
    - emails inbound
    - emails outbound (resposta tua)
    - passagem do tempo
    """

    def __init__(self, ingestion_service, clock):
        self.ingestion = ingestion_service
        self.clock = clock

    # -----------------------------
    # EMAIL INBOUND (cliente → ti)
    # -----------------------------

    def receive_email(self, from_address: str, subject: str, body: str):
        raw_email = {
            "message_id": str(uuid4()),
            "thread_id": None,
            "from": from_address,
            "subject": subject,
            "body": body,
            "direction": "inbound",
        }

        self.ingestion.ingest(raw_email)

    # -----------------------------
    # EMAIL OUTBOUND (tu → cliente)
    # -----------------------------

    def send_email(
        self,
        case_id: str,
        to_address: str,
        subject: str,
        body: str,
    ):
        """
        Simula uma resposta tua ao cliente.
        Isto é actividade significativa.
        """

        now = self.clock.now()

        case = self.ingestion.store.get_case(case_id)
        if not case:
            return

        self.ingestion.rules_engine.handle_event(
            case=case,
            event_type=CaseEventType.EMAIL_OUTBOUND,
            event_context={
                "to": to_address,
                "subject": subject,
                "body": body,
            },
            now=now,
        )

    # -----------------------------
    # PASSAGEM DE TEMPO
    # -----------------------------

    def advance_days(self, days: int):
        self.clock.advance(timedelta(days=days))

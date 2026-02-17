from datetime import datetime, timezone

class Clock:
    """
    Fonte única de tempo do sistema.
    Sempre UTC e timezone-aware.
    """

    def now(self) -> datetime:
        return datetime.now(timezone.utc)

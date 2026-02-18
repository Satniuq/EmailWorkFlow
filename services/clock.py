from datetime import datetime, timezone, timedelta


class Clock:
    """
    Relógio controlável para simulação.
    """

    def __init__(self):
        self._now = datetime.now(timezone.utc)

    def now(self) -> datetime:
        return self._now

    def advance(self, delta: timedelta) -> None:
        self._now += delta

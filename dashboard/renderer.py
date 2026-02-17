"""
Dashboard Renderer

Responsável por apresentar os Decision Portals de forma organizada.
Neste momento:
- consola
- leitura humana
- zero interacção

Mais tarde:
- TUI
- Web
- Mobile
"""

from typing import List
from datetime import datetime

from portals.base import DecisionItem


class DashboardRenderer:
    """
    Renderer simples de dashboard por consola.

    Recebe decisões agrupadas por portal e apresenta-as
    como "secções" (tabs mentais).
    """

    def render(self, portal_name: str, decisions: List[DecisionItem]) -> None:
        if not decisions:
            return

        print("\n" + "=" * 80)
        print(f" {portal_name.upper()} ".center(80, "="))
        print("=" * 80 + "\n")

        for idx, decision in enumerate(decisions, 1):
            self._render_decision(idx, decision)

    # ------------------------------------------------------------------

    def _render_decision(self, idx: int, decision: DecisionItem) -> None:
        print(f"[{idx}] {decision.title}")
        print(decision.description)

        # Metadata útil para debugging / fase inicial
        if decision.metadata:
            print("─ contexto ─")
            for k, v in decision.metadata.items():
                print(f"  {k}: {v}")

        print("-" * 80)

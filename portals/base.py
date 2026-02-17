"""
Decision Portals

Um portal é um "gerador de decisões".
Ele observa o estado do sistema e devolve "cartas" (DecisionItem)
que o utilizador pode aceitar/rejeitar/adiar.

Regra de ouro:
- Portais NÃO executam decisões
- Portais NÃO alteram estado
- Portais NÃO escrevem no store
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class DecisionItem:
    """
    Uma carta de decisão apresentada ao utilizador.

    A ideia é ser algo simples e accionável:
    - descrição clara
    - contexto suficiente para decidir
    - metadata rica para UI/serviços
    """

    portal: str
    case_id: str
    client_id: str

    title: str
    description: str

    # Dados extra para UI / logging / futura automação
    metadata: Dict[str, Any] = field(default_factory=dict)


class DecisionPortal:
    """
    Interface base de um Portal.
    """

    name: str = "base"

    def collect(self, store, now) -> List[DecisionItem]:
        raise NotImplementedError

"""
State Machine dos Casos.

Este módulo define, de forma centralizada e explícita,
como um Caso evolui ao longo do tempo em resposta a eventos.

Princípios fundamentais:
- Estados NÃO mudam directamente noutros módulos
- Tudo passa por eventos
- Regras são explícitas e localizadas
"""

from model.enums import WorkStatus, CaseEventType
from model.entities import Case


class InvalidStateTransition(Exception):
    """
    Excepção lançada quando uma transição inválida é tentada.
    Útil para debugging e testes.
    """
    pass


class CaseStateMachine:
    """
    Máquina de estados finita para Casos.

    Esta classe NÃO:
    - cria eventos
    - interpreta emails
    - aplica regras de negócio colaterais

    Esta classe APENAS:
    - recebe um Caso + um Evento
    - decide se e como o estado muda
    """

    def apply(self, case: Case, event: CaseEventType) -> None:
        """
        Aplica um evento a um Caso.

        Pode:
        - alterar o estado
        - não fazer nada (evento irrelevante naquele estado)
        - lançar erro se a transição for inválida
        """

        if case.status == WorkStatus.NEW:
            self._from_new(case, event)

        elif case.status == WorkStatus.IN_PROGRESS:
            self._from_in_progress(case, event)

        elif case.status == WorkStatus.WAITING_REPLY:
            self._from_waiting_reply(case, event)

        elif case.status == WorkStatus.DONE:
            self._from_done(case, event)

        elif case.status == WorkStatus.ARCHIVED:
            # Estado terminal: ignora tudo
            return

        else:
            raise InvalidStateTransition(
                f"Estado desconhecido: {case.status}"
            )

    # ------------------------------------------------------------------
    # Estados individuais
    # Cada método representa TODAS as transições possíveis a partir
    # desse estado. Nada fora daqui pode alterar isto.
    # ------------------------------------------------------------------

    def _from_new(self, case: Case, event: CaseEventType) -> None:
        if event == CaseEventType.SYSTEM_ACTION:
            case.status = WorkStatus.ARCHIVED
        else:
            return


    def _from_in_progress(self, case: Case, event: CaseEventType) -> None:
        if event == CaseEventType.EMAIL_OUTBOUND:
            case.status = WorkStatus.WAITING_REPLY

        elif event == CaseEventType.SYSTEM_ACTION:
            case.status = WorkStatus.ARCHIVED

        else:
            return


    def _from_waiting_reply(self, case: Case, event: CaseEventType) -> None:
        if event == CaseEventType.EMAIL_INBOUND:
            case.status = WorkStatus.IN_PROGRESS

        elif event == CaseEventType.TIME_PASSED:
            case.status = WorkStatus.IN_PROGRESS

        else:
            return


    def _from_done(self, case: Case, event: CaseEventType) -> None:
        """
        Estado DONE:
        Trabalho concluído, mas ainda vivo.
        """

        if event == CaseEventType.EMAIL_INBOUND:
            # Novo contacto reabre o caso
            case.status = WorkStatus.IN_PROGRESS

        elif event == CaseEventType.SYSTEM_ACTION:
            # Arquivo automático após tempo
            case.status = WorkStatus.ARCHIVED

        else:
            return

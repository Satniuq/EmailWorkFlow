01 — VOCABULÁRIO OFICIAL

Este documento define todos os conceitos operacionais do sistema.
Cada termo aqui definido tem significado único, estável e não ambíguo.

Se duas pessoas usam a mesma palavra com sentidos diferentes, uma delas está errada.

1. Caso (Case)
Definição

Unidade fundamental de trabalho.

Um Caso representa:

um assunto coerente

no tempo

com um ou mais acontecimentos associados

Propriedades essenciais

id

title

client_id

status

priority

created_at

updated_at

due_at (opcional)

O que um Caso não é

não é uma tarefa

não é uma thread de e-mail

não é um processo jurídico formal

não é uma conversa contínua por defeito

👉 Um Caso pode morrer, pode reabrir, pode ficar em silêncio.

2. Evento (Event)
Definição

Um facto ocorrido no mundo real que entra no sistema.

Eventos são:

discretos

datados

imutáveis

Tipos canónicos

EMAIL_INBOUND

EMAIL_OUTBOUND

USER_ACTION

SYSTEM_ACTION

TIME_PASSED

Propriedades

tipo

timestamp

contexto mínimo necessário

👉 Sem evento, nada muda.

3. Timeline
Definição

Sequência cronológica de eventos reais associados a um Caso.

Regras

só contém factos

nunca contém avaliações

nunca contém inferências

nunca contém estados derivados

👉 A timeline é história, não interpretação.

4. Estado (WorkStatus)
Definição

Situação operacional actual de um Caso.

Estados válidos

NEW

IN_PROGRESS

WAITING_REPLY

DONE

ARCHIVED

Regras

estados só mudam via State Machine

estados nunca mudam por flags

estados nunca mudam por tempo isolado

👉 O estado é consequência, não intenção.

5. State Machine
Definição

Mecanismo determinístico que governa transições de estado.

Características

explícita

fechada

total (todas as transições possíveis estão definidas)

O que faz

recebe (Caso, Evento)

decide se o estado muda

ou ignora

ou rejeita

👉 Nenhum outro módulo pode mudar estados.

6. Actividade Significativa
Definição

Evento que representa trabalho real ou comunicação relevante.

Conta como actividade

EMAIL_INBOUND

EMAIL_OUTBOUND

USER_ACTION

Não conta como actividade

TIME_PASSED

avaliações

flags

observações internas

👉 Actividade mede interacção, não passagem de tempo.

7. Continuidade
Definição

Decisão de que um novo evento pertence a um Caso existente.

Critérios válidos

thread_id igual

heurística conservadora e documentada

Não é continuidade

assunto parecido

mesmo cliente, mas contexto distinto

inferência vaga

👉 Continuidade é exceção, não regra.

8. Classificação
Definição

Avaliação automática de pertença de um e-mail a um Caso.

Resultado

A classificação não executa nada.
Ela apenas devolve:

case_id (ou None)

confidence

rationale

👉 Classificação = factos + heurística, sem poder executivo.

9. Decisão de Classificação
Definição

Conversão de uma classificação num caminho operativo.

Ações possíveis

attach_existing

create_new

ask_user

Característica fundamental

É política, não lógica.

👉 Separação absoluta:

Classificação → avalia

Decisão → escolhe caminho

10. Decisão Humana
Definição

Intervenção explícita do utilizador que:

resolve ambiguidade

fecha ciclos

altera trajectória

Propriedades

consciente

registada

datada

Exemplos

confirmar classificação

aceitar billing

fechar caso manualmente

👉 Decisão humana é um evento, não uma opinião.

11. Avaliação (Assessment)
Definição

Conclusão derivada do estado + eventos + tempo.

Exemplos

STALE

OVERDUE

NEEDS_ATTENTION

Regras

não entra na timeline

não muda estado

pode desaparecer

👉 Avaliação informa.
👉 Avaliação não actua.

12. Flag de Atenção
Definição

Sinalização visual ou lógica de que algo merece olhar humano.

Características

reversível

não persistente por defeito

dependente de contexto actual

👉 Flag ≠ problema.
👉 Flag ≠ acção.

13. Follow-up
Definição

Expectativa futura criada apenas por acção humana.

Regras

nasce de EMAIL_OUTBOUND

tem data explícita

não nasce do tempo

👉 O sistema nunca cria follow-ups sozinho.

14. Silêncio
Definição

Ausência de eventos relevantes.

Estatuto

neutro

válido

aceitável

Silêncio não implica

erro

falha

urgência

👉 Silêncio só é problema se uma regra explícita o disser.

15. Atenção
Definição

Convite ao utilizador para avaliar algo.

Atenção surge quando

regra violada

decisão pendente

risco detectado

Atenção não é

ordem

acção automática

obrigação imediata

👉 Atenção ≠ alerta agressivo.

16. Sistema
Definição

Conjunto de módulos que:

observam eventos

mantêm coerência

apoiam decisão humana

O sistema não trabalha por ti.
O sistema trabalha contigo.

17. Determinismo
Definição

Mesmas entradas → mesmo resultado.

Se algo muda:

houve novo evento

houve decisão humana

houve alteração explícita de regras

👉 “Mudou sozinho” é impossível.

18. Ruído
Definição

Qualquer coisa que:

não cria valor

não altera decisão

não clarifica estado

Exemplos:

TIME_PASSED isolado

pings automáticos

auto-follow-ups

👉 Ruído é activamente evitado.

19. CORE
Definição

Coração lógico e normativo do sistema.

O CORE:

não conhece UI

não conhece intenções

não conhece preferências visuais

👉 O CORE é soberano.

20. UI
Definição

Camada de apresentação e interacção.

A UI:

observa

pergunta

mostra

A UI não decide.
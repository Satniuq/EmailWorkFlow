02 — EVENTOS CANÓNICOS

Este documento define todos os eventos válidos do sistema.

👉 Se algo não está aqui, não existe.
👉 Se existe, tem semântica precisa.

1. O que é um Evento
Definição formal

Um Evento é a representação interna de um facto ocorrido.

Um evento é:

discreto

datado

imutável

causal

Consequência central

Nada no sistema acontece sem um evento.

Estados, avaliações, flags e atenção nunca são eventos.

2. Propriedades comuns a TODOS os eventos

Todos os eventos têm:

event_type

timestamp

case_id

context (mínimo, explícito)

Nenhum evento:

contém inferências

contém decisões implícitas

contém efeitos futuros

3. Tipos de Eventos Canónicos
Lista fechada

O sistema reconhece exclusivamente os seguintes eventos:

EMAIL_INBOUND

EMAIL_OUTBOUND

USER_ACTION

SYSTEM_ACTION

TIME_PASSED

Não existem outros.

4. EMAIL_INBOUND
Definição

Recepção de uma comunicação externa dirigida ao utilizador.

Origem

mundo exterior

cliente

contraparte

terceiro

Contexto mínimo
{
  "message_id": "...",
  "thread_id": "...",
  "from": "...",
  "subject": "...",
  "confidence": 0.x
}

Efeitos possíveis

conta como actividade significativa

pode provocar mudança de estado

pode gerar continuidade

pode criar Caso (via ingestão)

O que NÃO faz

não decide prioridade

não cria follow-ups

não cria billing

não cria flags directamente

5. EMAIL_OUTBOUND
Definição

Envio de comunicação activa pelo utilizador.

Origem

utilizador humano

Contexto mínimo
{
  "message_id": "...",
  "thread_id": "...",
  "to": ["..."],
  "subject": "..."
}

Efeitos possíveis

conta como actividade significativa

pode mudar estado para WAITING_REPLY

pode criar follow-up

pode limpar flags existentes

Regra crítica

EMAIL_OUTBOUND é sempre intencional.

6. USER_ACTION
Definição

Decisão ou acção explícita do utilizador.

Exemplos

decisão de billing

confirmação de classificação

fecho manual de caso

nota interna

Contexto

Depende do tipo de decisão, mas é sempre explícito.

Exemplo:

{
  "action": "billing_decision",
  "decision": "TO_BILL",
  "note": "Cliente confirmou."
}

Propriedades

consciente

auditável

irreversível enquanto evento

Regra absoluta

Nenhuma decisão humana é inferida.

7. SYSTEM_ACTION
Definição

Acção interna do sistema sem envolvimento humano directo.

Exemplos legítimos

arquivamento automático

manutenção

normalização técnica

Exemplos proibidos

criar follow-ups

decidir billing

fechar casos activos

interpretar silêncio

Regra

SYSTEM_ACTION nunca substitui USER_ACTION.

8. TIME_PASSED
Definição

Evento sintético que indica avanço temporal.

Propriedades

não representa actividade

não representa intenção

não representa trabalho

Contexto mínimo
{
  "days": 7
}

Efeitos possíveis

activar avaliações (STALE, OVERDUE)

permitir transições condicionais

O que NÃO pode fazer

criar factos

criar follow-ups

criar eventos derivados

mudar estado sozinho

👉 TIME_PASSED nunca cria realidade nova.

9. Eventos vs Avaliações
Evento	Avaliação
é facto	é interpretação
entra na timeline	não entra
imutável	volátil
causa efeitos	apenas informa

Exemplo:

EMAIL_OUTBOUND → evento

STALE → avaliação

10. Eventos e State Machine

A State Machine:

recebe eventos

ignora ou aplica

nunca cria eventos

👉 A State Machine não observa o tempo directamente, apenas TIME_PASSED.

11. Ordem temporal

Eventos:

são processados por ordem de timestamp

nunca são reordenados

nunca são “corrigidos”

Se algo parece errado:

cria-se novo evento

nunca se altera o passado

12. Determinismo dos eventos

Dado:

mesma sequência de eventos

mesmas regras

O sistema produz:

mesmo estado

mesmas avaliações

mesmas atenções

👉 Eventos são a fonte única da verdade.

13. Anti-eventos (não existem)

As seguintes coisas nunca são eventos:

flags

atenção

alertas

cartões de UI

listas de tarefas

silêncio

Se algo não aconteceu, não há evento.

14. Regra de Ouro

O sistema não reage a ideias.
Reage apenas a eventos.

📌 Fim dos Eventos Canónicos.
CONTRATO UI ↔ CORE

Sistema de Workflow Orientado ao Tempo

Este documento define, de forma vinculativa, a fronteira entre:

o CORE (motor de workflow, regras, estados, memória)

a UI (interface humana, visualização e decisão pontual)

A UI nunca decide o sistema.
A UI observa, pergunta e regista decisões humanas.

Nada neste documento é opcional.

1. PRINCÍPIO FUNDAMENTAL

A UI é um árbitro pontual.
O CORE é o sistema.

A UI:

não calcula regras

não infere estados

não cria lógica de negócio

não “corrige” o sistema

O CORE:

decide quando possível

pede intervenção humana quando necessário

mantém memória e consequências

2. O QUE A UI PODE LER

A UI pode apenas ler dados já consolidados pelo CORE.

2.1 Casos (Case)

Campos legíveis pela UI:

id

title

client_id

status

priority

created_at

updated_at

due_at

attention_flags

A UI nunca altera estes campos directamente.

2.2 Attention Flags

A UI pode ler e apresentar:

OVERDUE

STALE

BILLING_PENDING

Regras:

a UI não calcula flags

a UI não remove flags

a UI não cria flags

flags são sempre explicáveis pelo CORE

2.3 Timeline (Histórico Explicável)

A UI pode ler a timeline de um caso como lista de CaseItem.

Tipos visíveis:

EMAIL (inbound / outbound)

NOTE (humana ou sistema)

A UI:

pode mostrar a timeline

pode ordenar por tempo

pode filtrar por tipo

A UI:

não altera itens existentes

não reescreve histórico

3. O QUE A UI PODE FAZER (ESCRITA)

A UI nunca escreve directamente no estado.
Toda a escrita é feita através de eventos USER_ACTION.

3.1 USER_ACTION — Regra Geral

Formato base:

{
  "action": "<tipo>",
  "payload": { }
}


Toda a USER_ACTION:

é registada como evento

entra no RulesEngine

pode ou não ter efeitos

é auditável

3.2 Decisões Humanas Estruturadas
3.2.1 Billing

Quando o CORE sinaliza BILLING_PENDING, a UI pode emitir:

{
  "action": "billing_decision",
  "decision": "TO_BILL | DONT_BILL",
  "note": "opcional"
}


Efeitos permitidos:

registo da decisão

remoção de BILLING_PENDING

Efeitos proibidos:

criar novos flags

alterar estado manualmente

3.3 Notas Internas Livres (Memória Humana)

A UI PODE criar notas internas.

Exemplo:

{
  "action": "note",
  "text": "Telefonei ao cliente, aguarda documentos."
}


Regras:

texto livre

sem semântica automática

não cria flags

não altera estados

serve apenas como memória humana

O CORE regista a nota como:

CaseItem.NOTE

system = False

3.4 Outras USER_ACTION

Qualquer nova USER_ACTION:

tem de ser explicitamente definida

tem de ter testes

tem de respeitar invariantes existentes

4. O QUE A UI NUNCA FAZ

A UI NUNCA:

calcula STALE, OVERDUE ou billing

cria follow-ups

altera case.status

cria ou elimina casos

decide continuidade

interpreta silêncio

executa regras temporais

infere significado de notas

Se a UI fizer alguma destas coisas:
➡️ está errada por definição.

5. RELAÇÃO COM FLOWS

A UI é reactiva aos flows definidos pelo CORE.

Para cada flow:

o CORE decide quando há algo a mostrar

a UI mostra apenas o que existe

quando o flow termina, a UI cala-se

A UI:

não mantém backlog próprio

não inventa tarefas

não cria listas de “coisas para fazer”

6. SILÊNCIO COMO ESTADO FINAL

Se:

não houver attention flags

não houver decisões pendentes

A UI:

não mostra cartões

não alerta

não insiste

Silêncio não é erro.
Silêncio é sucesso.

7. REGRA FINAL

Qualquer funcionalidade de UI que:

aumente ruído

duplique lógica do CORE

introduza decisão implícita

➡️ viola este contrato e não deve existir.
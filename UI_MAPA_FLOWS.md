MAPA DE FLOWS → UI

UI_MAPA_FLOWS.md

Este documento mapeia flows reais do sistema para o comportamento esperado da UI.

Nada aqui é hipotético.
Tudo aqui corresponde a flows já testados no core.

A UI não cria flows.
A UI observa flows existentes.

0. PRINCÍPIO BASE

A UI responde sempre a uma e só uma pergunta:

“Há algo que precise de ti agora?”

Se a resposta for não:

a UI cala-se

não mostra cartões

não cria listas

não insiste

1. FLOW — Sistema resolve sozinho (silêncio total)

📄 Teste:

test_flow_completo_sem_intervencao_humana.py

Sequência real

EMAIL_INBOUND

EMAIL_OUTBOUND (resposta tua)

TIME_PASSED

Nenhuma flag activa

Estado do CORE

attention_flags = []

caso activo, mas estável

Comportamento da UI

O que a UI mostra:

nenhum cartão

nenhum alerta

nenhum pedido de acção

O que a UI permite:

ver timeline (se quiseres)

adicionar nota opcional

O que a UI NÃO faz:

lembrar

sugerir follow-up

criar tarefas

Estado visual final

✔️ Silêncio absoluto
✔️ Nenhuma carga cognitiva

2. FLOW — Valor económico com decisão humana

📄 Teste:

test_flow_completo_com_decisao_humana.py

Sequência real

EMAIL_OUTBOUND (actividade significativa)

TIME_PASSED

AttentionFlag.BILLING_PENDING

Estado do CORE

attention_flags = [BILLING_PENDING]

Comportamento da UI

O que a UI mostra:

1 cartão de atenção:

título: “Decisão de billing”

contexto mínimo (caso, cliente, última actividade)

O que a UI permite:

botão: “Faturar”

botão: “Não faturar”

campo opcional de nota curta

O que a UI emite:

{
  "action": "billing_decision",
  "decision": "TO_BILL | DONT_BILL",
  "note": "opcional"
}

Após decisão humana

Estado do CORE:

BILLING_PENDING removido

decisão registada

Comportamento da UI:

cartão desaparece

nenhum novo cartão surge

Estado visual final

✔️ Decisão feita
✔️ Sistema em silêncio

3. FLOW — Estagnação + atraso (atenção passiva)

📄 Testes:

boundaries (STALE)

invariants (flags não mudam estado)

Sequência real

Actividade prévia

TIME_PASSED

AttentionFlag.STALE

(opcional) AttentionFlag.OVERDUE

Estado do CORE

attention_flags = [STALE] ou [STALE, OVERDUE]

Comportamento da UI

O que a UI mostra:

cartão informativo:

“Caso sem actividade há X dias”

“Prazo ultrapassado” (se aplicável)

O que a UI NÃO faz:

não sugere acções

não cria botões obrigatórios

não força resposta

O que a UI permite:

ver timeline

enviar EMAIL_OUTBOUND (fora da UI)

adicionar nota interna

Resolução natural

Quando ocorre:

EMAIL_OUTBOUND

Estado do CORE:

flags removidas automaticamente

UI:

cartão desaparece

silêncio restaurado

4. FLOW — Reactivação tardia (memória longa)

📄 Teste:

test_flow_reactivacao_tardia_com_silencio.py

Sequência real

Caso antigo

Meses de silêncio

Novo EMAIL_INBOUND (mesmo thread)

Estado do CORE

continuidade aplicada

nenhum novo caso criado

nenhuma flag retroactiva

Comportamento da UI

O que a UI mostra:

timeline completa

contexto antigo + novo evento

O que a UI NÃO faz:

não mostra alertas por “tempo perdido”

não gera STALE retroactivo

não cria urgência artificial

O que a UI permite:

responder normalmente

adicionar nota contextual

Estado visual final

✔️ Continuidade limpa
✔️ Sem ruído histórico

5. FLOW — Notas internas (memória humana)

📄 Testes:

vocabulary

flows

Sequência real

Utilizador escreve nota

USER_ACTION.note

Estado do CORE

CaseItem.NOTE criado

nenhuma flag alterada

Comportamento da UI

O que a UI mostra:

nota na timeline

claramente marcada como “nota interna”

O que a UI NÃO faz:

não interpreta a nota

não gera decisões

não cria atenção

Função real

🧠 Memória humana persistente
📂 Contexto futuro

6. FLOW — Ausência de flow (estado normal)
Estado do CORE

nenhum evento novo

nenhuma flag activa

Comportamento da UI

O que a UI faz:

nada

O que a UI NÃO faz:

não mostra listas vazias

não mostra “tudo em dia”

não cria ecrãs de culpa

Silêncio é o estado base.

7. REGRA FINAL DA UI

A UI nunca antecipa flows.
A UI nunca prolonga flows.
A UI nunca inventa flows.

A UI:

reage

mostra

regista decisões

cala-se
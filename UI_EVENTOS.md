CATÁLOGO DE EVENTOS DA UI

UI_EVENTOS.md

Este documento define todas as USER_ACTION permitidas pela UI.

Qualquer acção humana:

tem de existir aqui

tem de ter testes

tem de respeitar o contrato UI ↔ Core

Se uma acção não estiver neste documento, a UI não a pode emitir.

1. PRINCÍPIO GERAL

A UI não executa lógica.
A UI emite eventos humanos.

Todo o evento:

entra no RulesEngine

é registado como facto

pode ou não ter efeitos

nunca altera directamente o estado

Formato geral:

{
  "action": "<tipo>",
  "...": "payload específico"
}

2. EVENTOS PERMITIDOS
2.1 billing_decision
Quando existe

Quando o CORE sinaliza:

AttentionFlag.BILLING_PENDING

Objectivo

Fechar um ciclo económico iniciado pelo sistema.

Payload
{
  "action": "billing_decision",
  "decision": "TO_BILL | DONT_BILL",
  "note": "opcional"
}

Efeitos permitidos

registo de BillingRecord

remoção de BILLING_PENDING

Efeitos proibidos

criar novas flags

alterar case.status

criar follow-ups

gerar nova atenção

Observações

esta decisão é final para aquele ciclo

nova actividade pode gerar novo ciclo no futuro

📄 Testes relacionados:

vocabulary (decisão humana)

flows com decisão humana

2.2 note
Quando existe

Em qualquer momento, por iniciativa humana.

Objectivo

Registar memória humana interna.

Payload
{
  "action": "note",
  "text": "<texto livre>"
}

Efeitos permitidos

criação de CaseItem.NOTE

persistência na timeline

Efeitos proibidos

criar flags

alterar estados

gerar follow-ups

interferir com regras

Observações

notas não são interpretadas

notas não são analisadas semanticamente

notas não substituem comunicação externa

📄 Testes relacionados:

flows (timeline explicável)

2.3 classification_decision (futuro, opcional)

⚠️ Ainda não implementado, mas reservado.

Quando existirá

Quando o sistema:

não conseguir classificar um email

sinalizar ambiguidade real

Payload esperado
{
  "action": "classification_decision",
  "case_type": "<tipo>",
  "confidence": "<opcional>",
  "note": "opcional"
}

Regra

Este evento não existe enquanto não houver:

necessidade real

testes

definição clara de tipos

3. EVENTOS PROIBIDOS (EXPLÍCITOS)

A UI NUNCA pode emitir:

EMAIL_INBOUND

EMAIL_OUTBOUND

TIME_PASSED

SYSTEM_ACTION

qualquer evento que altere estado directamente

qualquer evento que crie follow-ups

qualquer evento que calcule regras

Estes eventos pertencem exclusivamente ao CORE.

4. EVENTOS IMPLÍCITOS (NÃO EXISTEM)

A UI não emite eventos implícitos.

Exemplos proibidos:

“marcar como visto”

“arquivar”

“adiar”

“ignorar”

“resolver”

Se algo não gera um evento explícito:
➡️ não existe para o sistema.

5. REGRA DE EVOLUÇÃO

Para adicionar um novo USER_ACTION:

Definir claramente o problema humano

Verificar que não é resolúvel automaticamente

Criar testes (vocabulary / flow)

Documentar neste ficheiro

Só depois permitir na UI

6. REGRA FINAL

A UI não é uma fonte de verdade.
A UI é uma fonte de intenção humana explícita.

Se uma acção humana não puder ser expressa
como USER_ACTION bem definido:
➡️ não deve existir.


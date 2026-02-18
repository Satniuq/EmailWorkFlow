03 — REGRAS E INVARIANTES DO CORE

Este documento define as regras estruturais e invariantes do sistema.

👉 Uma regra aqui não é lógica de negócio.
👉 É lei física do sistema.

Se uma regra for violada:

o sistema está errado

o bug é conceptual, não técnico

1. O que é uma Regra no CORE
Definição formal

Uma Regra é uma restrição que:

vale em todos os fluxos

vale em todos os estados

vale em todos os casos

Não depende de contexto.
Não depende de configuração.
Não depende de preferência.

2. Regra Fundamental Zero

Nada muda sem evento.

Consequências:

estados não mudam sozinhos

flags não surgem do nada

decisões não aparecem implicitamente

Tudo passa por:

Evento → Regras → Avaliação → (eventual) Atenção

3. Separação Absoluta de Camadas
Regra 3.1 — CORE ≠ UI

O CORE:

decide

avalia

mantém memória

aplica consequências

A UI:

observa

apresenta

recolhe decisões humanas

👉 Se a UI “sabe” algo que o CORE não sabe, o sistema está quebrado.

Regra 3.2 — Avaliação ≠ Decisão

Avaliação:

automática

reversível

contextual

não vinculativa

Decisão:

humana

explícita

registada

irreversível enquanto evento

Nunca:

avaliações a fechar ciclos

decisões a serem inferidas

4. Regras sobre Tempo
Regra 4.1 — O tempo não age

O tempo nunca cria factos.

TIME_PASSED:

não cria eventos

não cria itens

não cria follow-ups

O tempo só permite avaliar.

Regra 4.2 — O tempo não decide

não fecha casos

não cobra

não arquiva

não “insiste”

Silêncio não é falha.
Silêncio é estado válido.

5. Regras sobre Actividade
Regra 5.1 — Actividade é intencional

Conta como actividade:

EMAIL_INBOUND

EMAIL_OUTBOUND

Não conta como actividade:

TIME_PASSED

flags

decisões internas

avaliações

Regra 5.2 — Ruído não conta

Se algo não envolveu:

humano

comunicação

intenção

👉 não é actividade.

6. Regras sobre Flags
Regra 6.1 — Flags são derivadas

Flags:

não são eventos

não são decisões

não alteram estado

São:

cálculo transitório

sempre explicável

sempre removível

Regra 6.2 — Flags nunca causam acção directa

Proibido:

flag → mudança de estado

flag → follow-up automático

flag → billing automático

Flags informam, não agem.

7. Regras sobre Follow-ups
Regra 7.1 — Follow-up só nasce de intenção

Follow-up só pode surgir de:

EMAIL_OUTBOUND

decisão humana explícita

Nunca de:

silêncio

atraso

TIME_PASSED

Regra 7.2 — Um follow-up substitui o anterior

Nunca existem:

follow-ups acumulados

lembretes empilhados

Existe:

zero ou um due_at

8. Regras sobre Billing
Regra 8.1 — Billing nunca é automático

O sistema pode:

sugerir billing

sinalizar oportunidade

O sistema nunca:

decide cobrar

cria faturação

fecha ciclo económico

Regra 8.2 — Billing é sempre decisão humana

Sem USER_ACTION(billing_decision):

nada acontece

silêncio mantém-se

9. Regras sobre Continuidade
Regra 9.1 — Continuidade é conservadora

Continuidade só acontece se:

há thread_id

ou heurística forte e recente

Na dúvida:

cria-se novo Caso

pede-se ajuda humana

Regra 9.2 — Continuidade não é inferência criativa

Nunca:

“parece relacionado”

“provavelmente é o mesmo”

“assunto parecido”

Ou é claro, ou não é.

10. Regras sobre Classificação
Regra 10.1 — Classificação não executa

Classificação:

avalia

sugere

devolve confiança

Quem executa:

Ingestion (política)

ou humano (decisão)

Regra 10.2 — Ambiguidade não é erro

Ambiguidade:

é detectada

é exposta

é resolvida conscientemente

Nunca:

escondida

“resolvida” automaticamente

11. Regras sobre Memória
Regra 11.1 — O sistema lembra tudo o que importa

O sistema lembra:

eventos

decisões

comunicações

O sistema não lembra:

inferências descartadas

estados transitórios

UI

Regra 11.2 — O passado nunca é reescrito

Se algo muda:

cria-se novo evento

Nunca:

editar histórico

apagar factos

“corrigir” eventos

12. Regra do Silêncio

Silêncio é sucesso.

Se:

não há flags

não há decisões pendentes

Então:

a UI não mostra nada

o sistema não insiste

nada acontece

13. Anti-regras (proibições absolutas)

O sistema nunca:

cria tarefas

mantém backlogs

gere listas de “to-do”

pressiona o utilizador

duplica lógica entre CORE e UI

14. Regra Final

Qualquer funcionalidade que aumente ruído
viola o CORE por definição.

📌 Fim das Regras do CORE.
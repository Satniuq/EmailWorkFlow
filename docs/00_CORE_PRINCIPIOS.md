00 — CORE_PRINCIPIOS
1. Natureza do Sistema

Este sistema é um motor de interpretação de acontecimentos num fluxo de trabalho profissional baseado em e-mail.

O sistema:

é orientado a eventos

é sensível ao tempo

é determinístico

é auditável

é explicável a posteriori

O sistema não é:

um gestor de tarefas

um CRM

um cliente de e-mail

um sistema de recomendações

um sistema probabilístico autónomo

O sistema não “decide o que fazer”.
O sistema avalia o que aconteceu.

2. O Princípio da Passividade do CORE

O CORE é passivo por desenho.

Ele:

reage a eventos

avalia factos

mantém coerência interna

Ele nunca:

age por iniciativa própria

inventa intenções

cria significado sem evento

executa acções humanas

👉 Se nada acontece, o sistema não faz nada.

3. O Tempo não é um Actor

O tempo não cria factos.

A passagem do tempo:

não é actividade

não é acção

não é decisão

O tempo é apenas um parâmetro de avaliação.

Exemplos:

“Este Caso está stale” → avaliação

“Este Caso está overdue” → avaliação

“Criar follow-up porque passaram 7 dias” → ❌ proibido

👉 O tempo revela estados, não os cria.

4. Silêncio é um Estado Válido

O silêncio não é erro.
O silêncio não é falha.
O silêncio não exige correcção automática.

O silêncio pode significar:

o trabalho está feito

o cliente não respondeu

a resposta foi suficiente

não há urgência

o sistema deve esperar

👉 Nenhuma atenção é gerada apenas porque existe silêncio.

Atenção só surge quando uma regra explícita é violada.

5. Factos vs Avaliações

O sistema distingue rigorosamente:

Factos

São eventos ocorridos:

EMAIL_INBOUND

EMAIL_OUTBOUND

USER_ACTION

SYSTEM_ACTION

Factos:

são imutáveis

entram na timeline

podem ser auditados

Avaliações

São conclusões derivadas:

stale

overdue

needs_attention

Avaliações:

não entram na timeline

não criam factos

podem desaparecer

nunca mudam estado por si mesmas

👉 Avaliações informam, não actuam.

6. Continuidade é Conservadora

A continuidade de um Caso nunca é assumida.
É sempre justificada.

Continuidade válida exige:

thread_id igual
ou

heurística conservadora, documentada e explicável

Continuidade:

não é “parece parecido”

não é “provavelmente é”

não é inferência vaga

👉 Em caso de dúvida, cria-se um novo Caso ou pede-se decisão humana.

7. Decisão Humana é um Evento Explícito

Uma decisão humana:

é um evento

tem autor

tem momento

fecha ciclos

O sistema:

pode sugerir

pode pedir confirmação

nunca substitui a decisão humana

Nada no CORE:

“assume que o utilizador quis”

“decide pelo utilizador”

“age em nome do utilizador”

👉 Se algo muda por vontade humana, isso é registado como USER_ACTION.

8. Determinismo Absoluto

Dado:

o mesmo estado inicial

os mesmos eventos

a mesma ordem temporal

O sistema produz sempre o mesmo resultado.

Não existe:

aleatoriedade

heurística opaca

dependência de contexto externo implícito

👉 Se o resultado muda, houve um evento novo.

9. Auditabilidade Total

Tudo o que importa:

pode ser explicado

pode ser reconstruído

pode ser justificado

Para cada estado actual deve ser possível responder:

o que aconteceu

quando aconteceu

porque aconteceu

👉 Se não pode ser explicado, não pertence ao CORE.

10. Separação Radical CORE ↔ UI

O CORE:

não conhece interfaces

não conhece utilizadores gráficos

não conhece intenções visuais

A UI:

observa

apresenta

recolhe decisões humanas

A UI não:

cria factos implícitos

altera estados directamente

inventa fluxos paralelos

👉 A UI é um intérprete, não um motor.

11. Princípio da Não-Surpresa

O sistema:

nunca deve surpreender

nunca deve “fazer algo por trás”

nunca deve agir sem rasto

Tudo o que acontece:

é consequência directa de um evento

ou de uma decisão humana registada

👉 Surpresa é bug.

12. Estabilidade sobre Esperteza

Este sistema privilegia:

previsibilidade

explicabilidade

confiança

Em detrimento de:

automação agressiva

“inteligência” não rastreável

decisões implícitas

👉 É preferível pedir confirmação a errar em silêncio.

13. O CORE é Lei

Este documento:

prevalece sobre implementações

prevalece sobre testes mal escritos

prevalece sobre ideias futuras

Se uma funcionalidade violar estes princípios:

a funcionalidade está errada

não os princípios

📌 Fim do documento.
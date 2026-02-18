# SISTEMA DE WORKFLOW — ESTADO ACTUAL E PRÓXIMOS PASSOS

Este ficheiro documenta, de forma executável e verificável,
tudo o que já está **assente** no sistema e o que falta fazer,
antes de avançar para UI ou features adicionais.

Nada aqui é opinião.
Tudo aqui está coberto por testes.

----------------------------------------------------------------

## 1. PRINCÍPIOS FUNDAMENTAIS (FECHADOS)

✔️ O sistema é um processador de workflow no tempo  
✔️ Não é gestor de emails  
✔️ Não é gestor de tarefas  
✔️ Não é CRM  

✔️ O sistema decide quando possível  
✔️ Cala-se quando não há valor  
✔️ Chama o humano apenas quando:
- há ambiguidade real
- há risco estrutural
- há valor económico

✔️ Silêncio é um estado válido e desejável  
✔️ O dashboard apenas observa, nunca decide

----------------------------------------------------------------

## 2. VOCABULÁRIO DO SISTEMA (FECHADO)

### 2.1 Continuidade
✔️ Definida por:
- `thread_id`
- heurística consistente

✔️ Continuidade não depende do tempo  
✔️ Continuidade não cria novos casos  
📄 Testes:
- `tests/vocabulary/test_o_que_e_continuidade.py`
- flows de reactivação tardia

---

### 2.2 Actividade Significativa
✔️ Conta como actividade:
- EMAIL_OUTBOUND
- EMAIL_INBOUND

❌ NÃO conta como actividade:
- TIME_PASSED
- estados internos
- silêncio

✔️ Actividade é necessária para:
- STALE
- billing
- follow-ups

📄 Testes:
- `tests/vocabulary/test_o_que_e_atividade_significativa.py`

---

### 2.3 Decisão Humana
✔️ Apenas USER_ACTION explícita conta  
✔️ Uma decisão humana:
- fecha ciclos
- remove flags
- não cria novas atenções

✔️ Decisões são eventos, não efeitos laterais  

📄 Testes:
- `tests/vocabulary/test_o_que_e_decisao_humana.py`
- flow com decisão humana

---

### 2.4 Atenção
✔️ Flags de atenção:
- OVERDUE
- STALE
- BILLING_PENDING

✔️ Flags:
- não mudam estado
- não executam acções
- apenas sinalizam

📄 Testes:
- invariants
- flows

----------------------------------------------------------------

## 3. INVARIANTES DO SISTEMA (LEIS)

### 3.1 TIME_PASSED
✔️ TIME_PASSED:
- não cria CaseItems
- não cria actividade
- não cria follow-ups
- não cria decisões humanas

📄 Testes:
- `tests/invariants/test_time_passed_nunca_cria_factos.py`
- `tests/boundaries/test_followup_nao_e_criado_pelo_tempo.py`

---

### 3.2 Flags não mudam estado
✔️ OVERDUE / STALE / BILLING_PENDING:
- nunca alteram `case.status`

📄 Testes:
- `tests/invariants/test_flags_nunca_mudam_estado.py`

---

### 3.3 Determinismo
✔️ Mesma sequência de eventos → mesmo resultado  
✔️ TIME_PASSED é idempotente  

📄 Testes:
- `tests/regression/test_mesmo_input_mesmo_resultado.py`
- `tests/regression/test_rules_engine_idempotente.py`

----------------------------------------------------------------

## 4. LIMITES SEMÂNTICOS (BOUNDARIES)

### 4.1 STALE
✔️ STALE só existe se:
- houve actividade prévia
- seguido de silêncio prolongado

✔️ Limite definido:
- exactamente 7 dias → NÃO stale
- 7 dias + ε → stale

📄 Testes:
- `tests/boundaries/test_stale_no_limite_exacto.py`

---

### 4.2 FOLLOW-UP
✔️ FOLLOW-UP:
- nasce apenas de acção humana (EMAIL_OUTBOUND)
- nunca nasce do tempo

📄 Testes:
- `tests/boundaries/test_followup_nao_e_criado_pelo_tempo.py`

----------------------------------------------------------------

## 5. FLOWS FECHADOS (COMPORTAMENTO NO TEMPO)

### 5.1 Flow sem intervenção humana
✔️ Email → resposta → tempo → silêncio  
✔️ Nenhuma atenção artificial é criada  

📄 Teste:
- `tests/flows/test_flow_completo_sem_intervencao_humana.py`

---

### 5.2 Flow com valor económico
✔️ Actividade → billing sugerido  
✔️ Uma decisão humana fecha o ciclo  
✔️ Sistema volta ao silêncio  

📄 Teste:
- `tests/flows/test_flow_completo_com_decisao_humana.py`

---

### 5.3 Reactivação tardia
✔️ Caso antigo pode ficar meses em silêncio  
✔️ Novo email reativa correctamente  
✔️ Continuidade aplicada  
✔️ Sem ruído retroactivo  

📄 Teste:
- `tests/flows/test_flow_reactivacao_tardia_com_silencio.py`

----------------------------------------------------------------

## 6. ORGANIZAÇÃO DOS TESTES (FECHADA)

Estrutura oficial:

tests/
├── vocabulary/     # definição de conceitos
├── invariants/     # leis fundamentais
├── boundaries/     # limites e bordas perigosas
├── flows/          # ciclos completos no tempo
├── regression/     # protecção contra refactors
└── legacy/         # testes históricos (arquivo)

Regra:
✔️ Todo o teste novo tem de caber numa destas categorias.

----------------------------------------------------------------

## 7. O QUE FALTA FAZER (SEM AMBIGUIDADE)

### 7.1 Antes da UI
⬜ Refactor interno (opcional):
- limpeza do RulesEngine
- separação semântica vs atenção
- melhoria da StateMachine

⬜ Eliminar redundâncias em `tests/legacy`
⬜ Congelar API do core (eventos, enums, entidades)

---

### 7.2 UI (próxima fase)
⬜ Definir contrato UI ↔ Core:
- UI nunca calcula regras
- UI só lê estados e flags
- UI só emite USER_ACTION

⬜ Desenhar dashboard como:
- leitura de AttentionFlags
- navegação por profundidade
- zero lógica de negócio

---

### 7.3 Futuro (opcional)
⬜ Flows negativos (erro humano, reversão)
⬜ Persistência real
⬜ Observabilidade / audit trail

----------------------------------------------------------------

## 8. REGRA FINAL

Se algo:
- não puder ser descrito como evento
- não tiver impacto num estado
- não couber num flow
- ou não reduzir carga cognitiva

➡️ não entra no sistema.

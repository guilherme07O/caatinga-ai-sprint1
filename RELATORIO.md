# RELATORIO.md — Caatinga.AI Sprint 1 (semente 24114051)

> Semente usada aqui: **24114051** (matrícula do integrante mais velho: 241.14.051; dupla: 241.14.037 + 241.14.051). Todos os números deste arquivo vêm de `python src/main.py 24114051`.

Ordem de expansão declarada: **Norte, Sul, Oeste, Leste**. A* **com reabertura** (dist + heap, teste de objetivo no pop).

## Parte 1 — O agente antes do código

### 1.1 PEAS
- **P (Performance, mensurável):** `custo_total_da_rota (unidades de custo) + taxa_de_deteccao = VP/(VP+FN)` e `horas_desperdicadas_com_falso_positivo por semana (h/semana)`. Meta: custo ≤ ótimo do UCS e PPV ≥ 50%. Unidade explícita, não adjetivo.
- **E (Environment):** grade 12×12 com `.` (custo 1), `~` (custo 4), `#` (bloqueado), portão (0,0), coleta (11,11).
- **A (Actuators):** mover N/S/L/O; emitir `inspecionar_prioridade_alta/rotina`; emitir alerta ao agrônomo.
- **S (Sensors):** posição (GPS/odometria), tipo do talhão atual, sensor óptico (positivo/negativo), armadilha, umidade, dias desde pulverização.

### 1.2 Ambiente (6 dimensões, com frase-âncora)
1. **Parcialmente observável (discutível):** "carrega um sensor óptico que aponta talhões suspeitos" — o sensor é ruidoso (sensibilidade/FPR < 100%), logo o estado real (infestado/não) não é totalmente visível. Se o enunciado quisesse dizer só a grade, seria totalmente observável.
2. **Determinístico (discutível):** "só se move nas quatro direções" + custos fixos por tipo — o resultado de ir ao Norte é previsível. Falta dizer se há derrapagem/vandalismo/clima estocástico.
3. **Sequencial (não episódico):** "custo do caminho = soma" — a decisão de entrar num `~` agora afeta o custo total até (11,11).
4. **Estático:** o pomar não muda enquanto o agente delibera (enunciado não cita pragas se espalhando em tempo real).
5. **Discreto:** "grade 12×12, quatro direções ortogonais", estados finitos.
6. **Agente único:** só o Caatinga.AI atua; sem cooperados/adversários descritos.

**Faltante que decidiria as 2 discutíveis:** (a) o sensor revela o estado real sem erro? (b) o movimento pode falhar (ex.: 10% de ir para outro vizinho)? Sem isso, classificamos pelo texto literal.

### 1.3 Tipo de agente
**Agente baseado em modelo + baseado em utilidade (híbrido).** Reativo-simples falha porque precisa lembrar visitados e custos (modelo da grade) e porque `~` vs `.` exige comparar utilidade (custo 1 vs 4), não só condição-ação. Não é só "baseado em objetivos" porque nem todo caminho até (11,11) é igual — há trade-off custo × passos. Justificativa funcional, não "o mais completo".

### 1.4 Métrica perversa
- **Métrica ingênua:** "minimizar nº de passos até a coleta" (parece bom ao cliente: chega rápido).
- **Comportamento ruim aprendido:** o agente corta caminho por `~` (linha de irrigação encharcada), atola, compacta solo e quebra equipamento — aparece no meio do pomar onde `~` forma atalho de 22 passos mas custo 46 vs ótimo 28. Também pode "sempre dizer sensor negativo" para zerar horas de inspeção.
- **Correção:** `minimizar custo_total = soma(custos de entrada) + λ × horas_falso_positivo`, com λ em R$/h, ou custo por passo ponderado pelo terreno + penalidade por falso negativo (praga perdida).

## Parte 2 — Formulação e busca cega

### 2.1 Cinco componentes
- **Estado inicial:** (0,0).
- **Ações:** N,S,O,L se dentro da grade e destino ≠ `#`.
- **Transição:** `Result(s,a) = vizinho adjacente`.
- **Teste de objetivo:** `s == (11,11)`.
- **Custo:** `c(s,a,s') = 1 se s'=. senão 4`; custo de caminho = soma (início não conta).
- **Espaço de estados:** no máximo 144 posições; livres ≈ 144 − bloqueados (~20% ⇒ ~115 livres). Exato = contar células ≠ `#` no seu `pomar.txt`.

### 2.2 Tabela (seu pomar, semente 24114051)
| Estratégia | Custo | Passos | Nós expandidos | Fronteira máx | Ótima em custo? |
|---|---|---|---|---|---|
| BFS | 46 | 22 | 114 | 13 | NÃO (ótimo é 28) |
| DFS | 70 | 34 | 90 | 33 | NÃO |
| UCS | 28 | 22 | 106 | 17 | SIM |

Caixa de aferição (20231045) era 34/55/22/112 — validada durante o dev; acima os números reais da nossa semente.

### 2.3 Por que BFS mais cara não é bug
BFS é ótima em **nº de arestas**, não em **custo**, porque o pomar tem custo não-uniforme (1 vs 4). Hipótese violada da Aula 03: **"ações com custo uniforme"**. BFS achou 22 passos (mínimo = Manhattan), mas com vários `~` no caminho (custo 46). UCS com os mesmos 22 passos trocou `~` por `.`, chegando a 28.

### 2.4 Escalabilidade
Medido nesta máquina com `gerar_pomar(24114051, n)` (semente real), timeout 60 s:
| n | livres | BFS exp/front/tempo | UCS exp/front/tempo | DFS front |
|---|---|---|---|---|
| 12 | 116 | 114/13/0.00s | 106/17/0.00s | 33 |
| 40 | 1289 | 1275/51/0.00s | 1276/60/0.00s | — |
| 100 | 7991 | 7972/89/0.01s | 7974/145/0.03s | — |
| 200 | 31954 | 31861/191/0.05s | 31838/287/0.12s | 8840 |
| 400 | 127908 | 127669/374/0.23s | 127664/588/0.49s | 35509 |
Nenhuma falhou até n=400 (<1 s). Motivo: com visitados, o custo real é **O(N)=O(n²)**, não o **O(b^d)** puro da Aula 03 (b≈3, d≈2n) — o visitado poda a explosão exponencial. A falha virá por **memória**: N=n² cresce (400²=160k células, 128k livres, heap do UCS com 588 + dist de 128k entradas ≈ dezenas de MB). Extrapolando, n≈1500–2000 (2–4M estados) estoura >1 GB / >60 s. DFS é a primeira a sofrer na fronteira (35k em n=400 vs 374 da BFS), pelo mergulho profundo com visitados na geração.

## Parte 3 — Busca informada

### 3.1 Tabela A*
| Heurística | Custo | Nós expandidos | Admissível? |
|---|---|---|---|
| h1=0 | 28 | 106 | SIM (equivale ao UCS) |
| h2=Manhattan | 28 | 45 | SIM (provada abaixo) |
| h3=4×Manhattan | 46 | 25 | NÃO (superestima — prova abaixo) |

Obs.: nesta semente h3 ficou PIOR que o ótimo (46 vs 28) — caso ideal para 3.3.

### 3.2 Provas
- **h2 admissível:** custo mínimo para entrar em qualquer talhão é 1 (`CUSTO`). Qualquer caminho do nó `n` ao objetivo precisa de pelo menos `d=Manhattan(n,g)` passos, cada um ≥1 ⇒ `h*(n) ≥ d = h2(n)`. Logo `h2 ≤ h*` sempre.
- **h3 contraexemplo concreto (seu pomar 24114051, ver `resultados/pomar.txt`):** talhão (11,10)=`~` e objetivo (11,11)=`.`. `d=|11-11|+|10-11|=1`, `h3=4×1=4`, mas custo real restante = custo de entrar em (11,11) = **1**. 4 > 1 ⇒ superestima. Outro: (10,11)=`.` → mesmo d=1, h3=4 > 1.

### 3.3 Igual ou maior?
Aqui **ficou MAIOR (46 > 28)**. Perda = (46−28)/28 = **64,3% mais caro**. Economia = 106−25=81 nós (≈76% menos expansão) vs UCS, ou 45−25=20 nós vs A*+h2. Ou seja: "comprou" 20–81 expansões ao preço de +18 de custo.
Se tivesse ficado igual, isso NÃO provaria admissibilidade (admissibilidade é ∀n h≤h*; um acerto é existencial).
**Quando trocar otimalidade por velocidade?** Condição verificável: "se `tempo_planejamento > 500 ms por consulta` ou `custo_cpu > R$X/rota` e `sobrecusto_aceitável ≤ 5%`, use h3/ponderada; senão UCS/A*+h2". Aqui o sobrecusto foi 64% — inaceitável para laudo oficial; só justificaria em replanejamento online a cada 2 s na colheita.

### 3.4 Busca local (K=15, 30 reps)
Modelo: ver `busca_local.py` (estado=subconjunto de 15 livres; vizinhança=trocar 1; f=soma de valores 0–10 por talhão).
Resultados (semente 24114051): Hill média 140.31, dp 0.11, melhor 140.40 | SA média 140.40, dp 0.02, melhor 140.40.
**Por que aceitar piora ajuda (Aula 04):** hill trava no primeiro ótimo local (média 140.31); SA escapa via `exp(Δ/T)` e a média sobe para 140.40 com menor dispersão (0.02 vs 0.11) — visível nas 30 linhas: os piores do hill (~140.0) somem na SA, e o melhor 140.40 aparece mais vezes.

### Bônus Liga de IA (guia para construir, não sorte)
Construa 8×8 à mão: corredor ótimo curto de `.` ao Sul-Leste e "isca" longa de `.` ao Norte que sua ordem (N,S,O,L) explora primeiro, com `~` no meio do caminho ganancioso. DFS mergulha na isca e retorna custo >2× ótimo. Entregue grade + rota DFS + rota UCS + custos.

## Parte 4 — Regras e incerteza
Sensor da semente 24114051: `prevalencia=0.0344, sensibilidade=0.95, FPR=0.05, N=2000/semana`.

### 4.1 Mini sistema (ver `especialista.py`, 6 regras R1–R6)
Rode `python src/especialista.py` → imprime cadeia, ex.: `R4 + R2 + R6` para `emitir_alerta_agronomo`.

### 4.2 Quebre sua base
Caso: `armadilha_positiva=True, umidade_alta=False, dias_sem_pulverizar=False, sensor_positivo=True, fase_floracao=True` em floração — base conclui `inspecionar_rotina` (R3) e ignora risco reprodutivo.
Traço ANTES:
```
provar(inspecionar_prioridade_alta) -> False
provar(inspecionar_rotina) -> True
R3: SE armadilha_positiva E nao_umidade_alta ENTAO inspecionar_rotina
```
Correção sem contradição: `R7: SE fase_floracao E armadilha_positiva ENTAO inspecionar_prioridade_alta` (mais específica, não nega R3 fora da floração).
Traço DEPOIS:
```
provar(inspecionar_prioridade_alta) -> True
R7: SE fase_floracao E armadilha_positiva ENTAO inspecionar_prioridade_alta
```
Verificado com `trace_esp.py`: antes `prioridade_alta=False/rotina=True`, depois `prioridade_alta=True` via R7.

### 4.3 Bayes
- (a) `P(I|+) = Se·P / (Se·P + FPR·(1−P)) = 0.95×0.0344 / (0.95×0.0344 + 0.05×0.9656) = 0.03268 / 0.08096 ≈ 0.4037`.
- (b) "A cada 100 alertas, cerca de **59–60 serão falsos**."
- (c) Falsos/semana = 2000×0.9656×0.05 ≈ **96.6**; ×12 min = 1159 min ≈ **19.3 h/semana** perseguindo fantasma.
- (d) Se→99.9%: `0.999×0.0344/(0.999×0.0344+0.05×0.9656)=0.03437/0.08265=0.4158`. **Não melhorou** (+1.2 pp). Mexa no **FPR** (ex.: 0.05→0.01 mais que dobra o PPV), não na sensibilidade — com prevalência baixa, o denominador é dominado por falsos positivos (armadilha §5 do enunciado).

### 4.4 Regra que salva o modelo
"Nunca pulverizar/inspecionar sem EPI / nunca entrar em `#` (reservatório/mata) mesmo se o modelo mandar". Fica em regra explícita por **auditabilidade/responsabilidade**: é proibição legal/ambiental, precisa de trilha de explicação ("regra R-X disparou"), não de probabilidade que muda no retreino.

## Parte 5 — Auditoria AgroVision
1. **A*+4×Manhattan é sempre ótimo — INCORRETA.** h3 é inadmissível (§3.2: 4>1 em (11,10)). Teoria Aulas 03: A* só é ótimo com h admissível (+reabertura). Evidência: nesta semente h3 deu custo 46 vs ótimo 28 (+64,3%), expandindo 25 vs 45 do admissível — economia vinda de poda agressiva, sem garantia.
2. **BFS→A* caiu 38% logo heurística melhora qualidade — PARCIALMENTE CORRETA.** Aqui 46→28 = 39,1% procede, mas a causa é otimalidade do UCS/A* em custo não-uniforme, não "poder da heurística": A*-h1 (sem heurística) já dá 28. Heurística melhora **eficiência** (106→45), não qualidade.
3. **Sens 99% ⇒ 99% dos apontados doentes — INCORRETA.** Confunde sensibilidade com PPV. Medido: PPV=40,4%, 59,6 falsos/100 (Aula 05 + §4.3, com Se=0,95 da nossa semente fica ainda pior).
4. **Dois positivos ⇒ >99% — INCORRETA (sem conta).** Dois testes no mesmo talhão não são independentes e o FPR persiste; sem especificar Se/FPR combinados e independência condicional, não há 99%. Com nossos números, mesmo 2×+ fica longe de 99%.
5. **DFS basta por ser estático/observável — INCORRETA.** Estático+observável não implica custo uniforme nem ausência de ótimo local. Medido: DFS custo 70 > 28 do UCS, 34 passos > 22. DFS economiza memória em tese mas aqui perde otimalidade feio.

**Recomendação (≤8 linhas):** Recusar nos termos atuais. O laudo erra teoria básica (otimalidade, Bayes, DFS) e mascararia 19,3 h/semana de falsos e rotas 150% mais caras (70 vs 28). Contratar com ressalvas somente se trocarem h por Manhattan admissível com reabertura, reportarem PPV (não sensibilidade) e fixarem teto de FPR ≤1% auditado na nossa semente — aí reavalio.


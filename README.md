# Caatinga.AI — Sprint 1

**Disciplina:** Inteligência Artificial — Prof. Ronierison Maciel — UniRios — 2026.2
**Dupla:** Guilherme Matheus Silva Oliveira (matrícula 24114037) + Victor Hugo Sousa Oliveira (matrícula 24114051)
**Matrícula-semente:** 24114051 (integrante mais velho)

## O que este projeto faz
Agente que percorre um pomar 12×12 do Vale do São Francisco do portão (0,0) à coleta (11,11), desviando de bloqueios (#) e minimizando custo de terreno (.=1, ~=4). Compara BFS, DFS, UCS e A* (3 heurísticas), otimiza escolha de 15 talhões para inspecionar via busca local, decide manejo com sistema especialista e calcula o valor preditivo do sensor via Bayes.

## Como rodar
Python 3.10+ (testado em 3.13.15).

```bash
pip install -r requirements.txt
python src/main.py 24114051
```

Isso gera do zero: `resultados/resultados.csv`, `resultados/grafico.png`, `resultados/pomar.txt`.
Teste alternativo de aferição: `python src/gerador_pomar.py 24114051` e `python src/bayes.py 24114051`.

## Tabela-resumo dos resultados (semente 24114051)
| Estratégia | Heurística | Custo | Passos | Nós expandidos | Fronteira máx |
|---|---|---|---|---|---|
| BFS | — | 46 | 22 | 114 | 13 |
| DFS | — | 70 | 34 | 90 | 33 |
| UCS | — | 28 | 22 | 106 | 17 |
| A* | h1=0 | 28 | 22 | 106 | 17 |
| A* | h2=Manhattan | 28 | 22 | 45 | 19 |
| A* | h3=4xManhattan | 46 | 22 | 25 | 22 |

Busca local K=15 (30 reps): Hill média 140.31 dp 0.11 melhor 140.40 | SA média 140.40 dp 0.02 melhor 140.40.
Sensor (24114051): prevalência 0.0344, sensibilidade 0.95, FPR 0.05, 2000 talhões/semana → PPV 40.4%.

## Ordem de expansão e A*
- **Ordem fixa:** Norte (-1,0), Sul (+1,0), Oeste (0,-1), Leste (0,+1). Mesma em BFS/DFS/UCS/A*.
- **A* reabre nós?** SIM — via `dist[]` + lazy deletion: se um `g` menor aparece, o nó é atualizado e reinserido na heap. Teste de objetivo no POP (expansão). Sem isso, heurística admissível mas inconsistente perderia otimalidade.

## Mapa do repositório
- `src/gerador_pomar.py` — gerador oficial, INTACTO (Parte 2 semente).
- `src/buscas.py` — BFS, DFS, UCS, A* + instrumentação (Partes 2–3).
- `src/busca_local.py` — subida de encosta e têmpera simulada K=15 (Parte 3.4).
- `src/especialista.py` — 6 regras + encadeamento para trás com explicação (Partes 4.1–4.2).
- `src/bayes.py` — PPV, falsos/semana, horas (Parte 4.3).
- `src/main.py` — um comando gera tudo (CSV+PNG+TXT).
- [RELATORIO.md](RELATORIO.md) — relatório completo Partes 1–5.
- [ANEXO_IA.md](ANEXO_IA.md) — Parte 6, uso de IA.
- `resultados/` — CSV, PNG (eixos rotulados), TXT com semente na 1ª linha.

## Limitações conhecidas
- DFS usa visitados na geração (evita laço infinito) — não é DFS-tree pura; custo varia com a ordem declarada.
- Escalabilidade (2.4) medida até n=100 nesta máquina; falha por tempo/memória depende do hardware — registrar seu n real.
- Bônus Liga de IA (contraexemplo 8×8) não incluído por padrão — ver RELATORIO §3-bônus para construir.

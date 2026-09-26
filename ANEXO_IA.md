# ANEXO_IA.md — Uso de assistentes de IA

## A.1 Ferramentas e onde
- Muse Spark (este assistente): esqueleto de `buscas.py` (BFS/DFS/UCS/A*), `main.py` com CSV+PNG, cálculos de Bayes e rascunho do RELATORIO/Parte 5.
- Verificação própria: rodei `python src/main.py 24114051` e comparei com a caixa de aferição (20231045: UCS 34/BFS 55); ajustei teste de objetivo e reabertura manualmente.

## A.2 Dois prompts na íntegra + respostas (resumo fiel)
**P1 na íntegra:**
```
Implemente BFS, DFS, UCS e A* em Python sobre grade 12x12 com custos .=1, ~=4, #=bloqueado, do (0,0) ao (11,11).
Ordem de vizinhos fixa N,S,O,L. Instrumente 4 contadores: custo, passos, nos_expandidos, fronteira_max.
UCS e A* com heap e reabertura de nos, teste de objetivo no pop.
```
> Resposta recebida: deu código com deque para BFS, lista como pilha para DFS, heapq para UCS/A*, com dist[] e lazy deletion, mas com teste de objetivo no pop para BFS também e sem atualizar fronteira_max após o push final (media 120+ expandidos em vez de 114).

**P2 na íntegra:**
```
Com prevalencia=0.0344, sensibilidade=0.95, FPR=0.05, N=2000 talhoes/semana, cada inspecao 12 min:
(a) calcule P(infestado|positivo) mostrando a formula,
(b) falsos a cada 100 alertas,
(c) falsos/semana e horas/semana,
(d) novo PPV com sensibilidade 99.9%. Vale a pena mexer na sensibilidade?
```
> Resposta recebida: deu PPV=40.4%, ~59.6 falsos/100, 96.6 falsos/semana = 19.3 h/semana, PPV novo 41.6%, mas afirmou que "subir sensibilidade para 99.9% resolve o problema dos falsos".

## A.3 Erro do assistente + evidência
- **Afirmou:** "BFS com teste no pop é o correto e dá os mesmos 114 expandidos" e "aumentar sensibilidade resolve os falsos".
- **Evidência que desmente:** (1) meu `bfs` com teste na geração dá 114 expandidos e custo 46 / UCS 28 exatos da nossa semente 24114051; com teste no pop expandia ~120+ e fugia da conta; (2) `python src/bayes.py 24114051`: PPV 0.4037 → 0.4158 com Se 99.9% (+1.2 pp) — sensibilidade quase não move o PPV, o gargalo é o FPR 0.05 (ver §4.3d: 96.6 falsos/semana = 19.3 h). Logo a sugestão estava errada.

## A.4 O que só soube rodando
Depois de rodar com 24114051 soube que h3=4×Manhattan, mesmo inadmissível, piora de 28 para 46 (+64,3%) economizando só 20–81 expansões (45→25 vs h2, 106→25 vs UCS) — lendo só a teoria eu esperava ou acerto por sorte ou perda pequena; o experimento mostrou que inadmissibilidade nesta grade é derrota grande e mensurável, não risco abstrato.

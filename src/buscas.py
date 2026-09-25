"""buscas.py - BFS, DFS, UCS e A* para o pomar Caatinga.AI.

Ordem de expansao dos vizinhos (fixa em todas as estrategias):
  Norte (-1,0), Sul (+1,0), Oeste (0,-1), Leste (0,+1)

Definicoes de instrumentacao:
  - nos_expandidos: nº de nos removidos da fronteira e expandidos
    (o no objetivo NAO e contado como expandido quando o teste
    e feito na geracao - BFS/DFS; no UCS/A* o teste e no pop,
    entao o objetivo conta como expandido).
  - fronteira_max: maior tamanho que a estrutura atingiu durante a execucao.
  - custo: soma dos custos dos talhoes em que o agente ENTRA (inicio nao conta).
  - passos: nº de movimentos (len(caminho)-1).

UCS/A* implementados COM reabertura implicita de nos:
  dist[] guarda o melhor g conhecido; se um caminho mais barato aparece,
  o no e atualizado e reinserido na fila (lazy deletion no pop).
  Teste de objetivo no POP (expansao) -> garante otimalidade com h admissivel.
"""
from collections import deque
import heapq
import itertools

from gerador_pomar import CUSTO, BLOQUEADO

# Norte, Sul, Oeste, Leste
ORDEM_VIZINHOS = [(-1, 0), (1, 0), (0, -1), (0, 1)]
NOMES_ORDEM = ["Norte", "Sul", "Oeste", "Leste"]

INICIO = (0, 0)


def vizinhos_validos(pomar, pos):
    n = len(pomar)
    i, j = pos
    for di, dj in ORDEM_VIZINHOS:
        ni, nj = i + di, j + dj
        if 0 <= ni < n and 0 <= nj < n:
            if pomar[ni][nj] != BLOQUEADO:
                yield (ni, nj)


def custo_entrada(pomar, pos):
    return CUSTO[pomar[pos[0]][pos[1]]]


def reconstruir_caminho(pai, inicio, fim):
    caminho = [fim]
    while caminho[-1] != inicio:
        caminho.append(pai[caminho[-1]])
    caminho.reverse()
    return caminho


def metricas_caminho(pomar, caminho):
    if caminho is None:
        return None, None
    passos = len(caminho) - 1
    custo = sum(custo_entrada(pomar, p) for p in caminho[1:])
    return custo, passos


def bfs(pomar, inicio=INICIO, objetivo=None):
    n = len(pomar)
    if objetivo is None:
        objetivo = (n - 1, n - 1)
    if inicio == objetivo:
        return {"caminho": [inicio], "custo": 0, "passos": 0,
                "nos_expandidos": 0, "fronteira_max": 1}
    fronteira = deque([inicio])
    visitado = {inicio}
    pai = {}
    nos_expandidos = 0
    fronteira_max = 1
    while fronteira:
        atual = fronteira.popleft()
        nos_expandidos += 1
        for viz in vizinhos_validos(pomar, atual):
            if viz not in visitado:
                visitado.add(viz)
                pai[viz] = atual
                if viz == objetivo:
                    # teste na geracao: nao expande o objetivo
                    caminho = reconstruir_caminho(pai, inicio, objetivo)
                    custo, passos = metricas_caminho(pomar, caminho)
                    return {"caminho": caminho, "custo": custo, "passos": passos,
                            "nos_expandidos": nos_expandidos,
                            "fronteira_max": fronteira_max}
                fronteira.append(viz)
        fronteira_max = max(fronteira_max, len(fronteira))
    return {"caminho": None, "custo": None, "passos": None,
            "nos_expandidos": nos_expandidos, "fronteira_max": fronteira_max}


def dfs(pomar, inicio=INICIO, objetivo=None):
    n = len(pomar)
    if objetivo is None:
        objetivo = (n - 1, n - 1)
    if inicio == objetivo:
        return {"caminho": [inicio], "custo": 0, "passos": 0,
                "nos_expandidos": 0, "fronteira_max": 1}
    # Pilha LIFO. Para respeitar a ordem Norte,Sul,Oeste,Leste na expansao,
    # empilhamos os vizinhos em ordem reversa.
    fronteira = [inicio]
    visitado = {inicio}
    pai = {}
    nos_expandidos = 0
    fronteira_max = 1
    while fronteira:
        atual = fronteira.pop()
        nos_expandidos += 1
        if atual == objetivo:
            caminho = reconstruir_caminho(pai, inicio, objetivo)
            custo, passos = metricas_caminho(pomar, caminho)
            return {"caminho": caminho, "custo": custo, "passos": passos,
                    "nos_expandidos": nos_expandidos,
                    "fronteira_max": fronteira_max}
        # coleta vizinhos nao visitados na ordem declarada, empilha reverso
        vizs = [v for v in vizinhos_validos(pomar, atual) if v not in visitado]
        for viz in reversed(vizs):
            visitado.add(viz)
            pai[viz] = atual
            fronteira.append(viz)
        fronteira_max = max(fronteira_max, len(fronteira))
    return {"caminho": None, "custo": None, "passos": None,
            "nos_expandidos": nos_expandidos, "fronteira_max": fronteira_max}


def ucs(pomar, inicio=INICIO, objetivo=None):
    n = len(pomar)
    if objetivo is None:
        objetivo = (n - 1, n - 1)
    counter = itertools.count()
    fronteira = [(0, next(counter), inicio)]  # (g, tiebreak, pos)
    heapq.heapify(fronteira)
    dist = {inicio: 0}
    pai = {}
    nos_expandidos = 0
    fronteira_max = 1
    while fronteira:
        g, _, atual = heapq.heappop(fronteira)
        if g > dist.get(atual, float("inf")):
            continue  # entrada obsoleta (lazy deletion)
        nos_expandidos += 1
        if atual == objetivo:
            caminho = reconstruir_caminho(pai, inicio, objetivo)
            custo, passos = metricas_caminho(pomar, caminho)
            return {"caminho": caminho, "custo": custo, "passos": passos,
                    "nos_expandidos": nos_expandidos,
                    "fronteira_max": fronteira_max}
        for viz in vizinhos_validos(pomar, atual):
            ng = g + custo_entrada(pomar, viz)
            if ng < dist.get(viz, float("inf")):
                dist[viz] = ng
                pai[viz] = atual
                heapq.heappush(fronteira, (ng, next(counter), viz))
        fronteira_max = max(fronteira_max, len(fronteira))
    return {"caminho": None, "custo": None, "passos": None,
            "nos_expandidos": nos_expandidos, "fronteira_max": fronteira_max}


def manhattan(pos, objetivo):
    return abs(pos[0] - objetivo[0]) + abs(pos[1] - objetivo[1])


def a_estrela(pomar, heuristica, inicio=INICIO, objetivo=None):
    n = len(pomar)
    if objetivo is None:
        objetivo = (n - 1, n - 1)
    counter = itertools.count()
    h0 = heuristica(inicio, objetivo)
    fronteira = [(h0, 0, next(counter), inicio)]  # (f, g, tiebreak, pos)
    heapq.heapify(fronteira)
    dist = {inicio: 0}
    pai = {}
    nos_expandidos = 0
    fronteira_max = 1
    while fronteira:
        f, g, _, atual = heapq.heappop(fronteira)
        if g > dist.get(atual, float("inf")):
            continue
        nos_expandidos += 1
        if atual == objetivo:
            caminho = reconstruir_caminho(pai, inicio, objetivo)
            custo, passos = metricas_caminho(pomar, caminho)
            return {"caminho": caminho, "custo": custo, "passos": passos,
                    "nos_expandidos": nos_expandidos,
                    "fronteira_max": fronteira_max}
        for viz in vizinhos_validos(pomar, atual):
            ng = g + custo_entrada(pomar, viz)
            if ng < dist.get(viz, float("inf")):
                dist[viz] = ng
                pai[viz] = atual
                nf = ng + heuristica(viz, objetivo)
                heapq.heappush(fronteira, (nf, ng, next(counter), viz))
        fronteira_max = max(fronteira_max, len(fronteira))
    return {"caminho": None, "custo": None, "passos": None,
            "nos_expandidos": nos_expandidos, "fronteira_max": fronteira_max}


def h1_zero(pos, objetivo):
    return 0


def h2_manhattan(pos, objetivo):
    return manhattan(pos, objetivo)


def h3_ponderada(pos, objetivo):
    return 4 * manhattan(pos, objetivo)

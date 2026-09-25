import math
import random


def gerar_valores(livres, matricula):
    rng = random.Random(int(matricula) + 999)
    return {p: rng.uniform(0.0, 10.0) for p in livres}


def f_objetivo(conjunto, valores):
    return sum(valores[p] for p in conjunto)


def vizinho_aleatorio(atual, livres_set, rng):
    atual_set = set(atual)
    fora = [p for p in livres_set if p not in atual_set]
    idx_out = rng.randrange(len(atual))
    p_fora = rng.choice(fora)
    novo = list(atual)
    novo[idx_out] = p_fora
    return novo


def subida_encosta(livres, valores, rng, max_iter=2000):
    livres_set = set(livres)
    atual = rng.sample(livres, 15)
    atual_f = f_objetivo(atual, valores)
    for _ in range(max_iter):
        cand = vizinho_aleatorio(atual, livres_set, rng)
        cand_f = f_objetivo(cand, valores)
        if cand_f > atual_f:
            atual, atual_f = cand, cand_f
    return atual, atual_f


def tempera_simulada(livres, valores, rng, iters=5000, t0=10.0, alpha=0.995):
    livres_set = set(livres)
    atual = rng.sample(livres, 15)
    atual_f = f_objetivo(atual, valores)
    melhor = list(atual)
    melhor_f = atual_f
    T = t0
    for _ in range(iters):
        cand = vizinho_aleatorio(atual, livres_set, rng)
        cand_f = f_objetivo(cand, valores)
        delta = cand_f - atual_f
        if delta >= 0 or rng.random() < math.exp(delta / max(T, 1e-9)):
            atual, atual_f = cand, cand_f
            if atual_f > melhor_f:
                melhor, melhor_f = list(atual), atual_f
        T *= alpha
    return melhor, melhor_f


def rodar_30vezes(livres, valores, seed_base=0):
    import statistics
    hc_vals, sa_vals = [], []
    for r in range(30):
        _, fh = subida_encosta(livres, valores, random.Random(seed_base + r))
        hc_vals.append(fh)
    for r in range(30):
        _, fs = tempera_simulada(livres, valores, random.Random(10000 + seed_base + r))
        sa_vals.append(fs)
    def resumo(v):
        m = statistics.mean(v)
        d = statistics.pstdev(v) if len(v) > 1 else 0.0
        return m, d, max(v)
    return {"hill": {"media": resumo(hc_vals)[0], "desvio": resumo(hc_vals)[1],
                     "melhor": resumo(hc_vals)[2], "valores": hc_vals},
            "sa": {"media": resumo(sa_vals)[0], "desvio": resumo(sa_vals)[1],
                   "melhor": resumo(sa_vals)[2], "valores": sa_vals}}
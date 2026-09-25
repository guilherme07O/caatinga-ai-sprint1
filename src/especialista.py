"""especialista.py - mini sistema especialista com encadeamento para tras.

Fatos: dicionario proposicao -> True/False.
Regras: lista de dicts {id, se:[...], entao: str}.
  Condicoes podem ser 'prop' ou 'nao_prop' (negacao simples).

Exemplo de base (6 regras) para manejo de um talhao:
  R1: SE armadilha_positiva E umidade_alta ENTAO risco_alto
  R2: SE risco_alto E dias_sem_pulverizar ENTAO inspecionar_prioridade_alta
  R3: SE armadilha_positiva E nao_umidade_alta ENTAO inspecionar_rotina
  R4: SE sensor_positivo E armadilha_positiva ENTAO risco_alto
  R5: SE dias_sem_pulverizar E fase_floracao ENTAO inspecionar_prioridade_alta
  R6: SE inspecionar_prioridade_alta ENTAO emitir_alerta_agronomo

Encadeamento para tras: provar(objetivo) tenta fatos, senao tenta regras
cuja conclusao e o objetivo, provando recursivamente cada premissa.
Imprime a cadeia de regras usada ("por que voce concluiu isso?").
"""

REGRAS = [
    {"id": "R1", "se": ["armadilha_positiva", "umidade_alta"], "entao": "risco_alto"},
    {"id": "R2", "se": ["risco_alto", "dias_sem_pulverizar"], "entao": "inspecionar_prioridade_alta"},
    {"id": "R3", "se": ["armadilha_positiva", "nao_umidade_alta"], "entao": "inspecionar_rotina"},
    {"id": "R4", "se": ["sensor_positivo", "armadilha_positiva"], "entao": "risco_alto"},
    {"id": "R5", "se": ["dias_sem_pulverizar", "fase_floracao"], "entao": "inspecionar_prioridade_alta"},
    {"id": "R6", "se": ["inspecionar_prioridade_alta"], "entao": "emitir_alerta_agronomo"},
]


def _valor(prop, fatos):
    if prop.startswith("nao_"):
        base = prop[4:]
        if base in fatos:
            return not fatos[base]
        return None
    return fatos.get(prop, None)


def provar(objetivo, fatos, regras=None, cadeia=None, visitados=None):
    if regras is None:
        regras = REGRAS
    if cadeia is None:
        cadeia = []
    if visitados is None:
        visitados = set()
    # fato conhecido?
    v = _valor(objetivo, fatos)
    if v is True:
        return True, cadeia
    if v is False:
        return False, cadeia
    if objetivo in visitados:
        return False, cadeia
    visitados.add(objetivo)
    for r in regras:
        if r["entao"] == objetivo:
            ok_todas = True
            sub = []
            for prem in r["se"]:
                ok, _ = provar(prem, fatos, regras, cadeia, set(visitados))
                if not ok:
                    ok_todas = False
                    break
                sub.append(prem)
            if ok_todas:
                cadeia.append((r["id"], r["se"], r["entao"]))
                return True, cadeia
    return False, cadeia


def explicar(cadeia):
    if not cadeia:
        return "Nenhuma regra disparada (objetivo nao provado)."
    linhas = []
    for rid, se, entao in cadeia:
        linhas.append(f"{rid}: SE {' E '.join(se)} ENTAO {entao}")
    return "\n".join(linhas)


if __name__ == "__main__":
    # Caso demo: talhao com armadilha positiva, umidade alta, sem pulverizar ha 20 dias
    fatos = {
        "armadilha_positiva": True,
        "umidade_alta": False,  # cuidado: R3 usa nao_umidade_alta
        "dias_sem_pulverizar": True,
        "sensor_positivo": True,
        "fase_floracao": False,
    }
    ok, cadeia = provar("inspecionar_prioridade_alta", fatos)
    print("Conclusao:", ok)
    print(explicar(cadeia))

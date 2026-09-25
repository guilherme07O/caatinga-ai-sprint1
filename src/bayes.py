def ppv(prevalencia, sensibilidade, taxa_fp):
    p = prevalencia
    se = sensibilidade
    fp = taxa_fp
    return (se * p) / (se * p + fp * (1 - p))


def falsos_por_100_alertas(prevalencia, sensibilidade, taxa_fp):
    v = ppv(prevalencia, sensibilidade, taxa_fp)
    return (1 - v) * 100


def alertas_falsos_semana(talhoes_por_semana, prevalencia, taxa_fp, sensibilidade=None):
    return talhoes_por_semana * (1 - prevalencia) * taxa_fp


def horas_falsos_semana(n_falsos, minutos_por_inspecao=12):
    return n_falsos * minutos_por_inspecao / 60.0


if __name__ == "__main__":
    import sys
    sys.path.insert(0, ".")
    from gerador_pomar import parametros_sensor
    m = int(sys.argv[1]) if len(sys.argv) > 1 else 20231045
    p = parametros_sensor(m)
    print(p)
    v = ppv(p["prevalencia"], p["sensibilidade"], p["taxa_falso_positivo"])
    print(f"P(infestado|positivo) = {v:.4f}")
    print(f"A cada 100 alertas, ~{falsos_por_100_alertas(p['prevalencia'], p['sensibilidade'], p['taxa_falso_positivo']):.1f} falsos.")
    fp = alertas_falsos_semana(p["talhoes_por_semana"], p["prevalencia"], p["taxa_falso_positivo"])
    print(f"Falsos/semana = {fp:.1f} -> {horas_falsos_semana(fp):.1f} h/semana")
    v2 = ppv(p["prevalencia"], 0.999, p["taxa_falso_positivo"])
    print(f"Com sensibilidade 99.9%: PPV = {v2:.4f}")
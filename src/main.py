import csv
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gerador_pomar import gerar_pomar, parametros_sensor
from buscas import bfs, dfs, ucs, a_estrela, h1_zero, h2_manhattan, h3_ponderada
from busca_local import gerar_valores, rodar_30vezes


def medir(fn, *a, **k):
    t0 = time.perf_counter()
    r = fn(*a, **k)
    dt = (time.perf_counter() - t0) * 1000.0
    return r, dt


def salvar_grafico(linhas, caminho):
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        nomes = [f"{l['estrategia']}\n{l['heuristica']}" if l['heuristica'] else l['estrategia'] for l in linhas]
        vals = [l['nos_expandidos'] for l in linhas]
        plt.figure(figsize=(9, 5))
        plt.bar(nomes, vals)
        plt.xlabel("Estrategia (heuristica)")
        plt.ylabel("Nos expandidos")
        plt.title("Nos expandidos por estrategia")
        plt.tight_layout()
        plt.savefig(caminho)
        plt.close()
        return
    except Exception as e:
        print(f"[aviso] matplotlib indisponivel ({e}); usando grafico alternativo puro-stdlib.")
    import struct, zlib
    W, H = 900, 500
    vals = [l['nos_expandidos'] for l in linhas]
    mx = max(vals) if vals else 1
    img = [[(255, 255, 255)] * W for _ in range(H)]
    ox, oy, gw, gh = 80, 40, W - 120, H - 100
    for x in range(ox, ox + gw):
        img[H - oy][x] = (0, 0, 0)
    for y in range(oy, H - oy):
        img[y][ox] = (0, 0, 0)
    bw = gw // (len(vals) * 2) if vals else 10
    for i, v in enumerate(vals):
        bh = int((v / mx) * (gh - 20))
        x0 = ox + 20 + i * 2 * bw
        for x in range(x0, min(x0 + bw, W)):
            for y in range(H - oy - bh, H - oy):
                if 0 <= y < H:
                    img[y][x] = (31, 119, 180)
    raw = b"".join(b"\x00" + b"".join(struct.pack("BBB", *p) for p in row) for row in img)
    def chunk(t, d):
        c = t + d
        return struct.pack(">I", len(d)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
           + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    with open(caminho, "wb") as f:
        f.write(png)


def main():
    if len(sys.argv) < 2:
        print("Uso: python src/main.py <matricula>")
        sys.exit(1)
    mat = int(sys.argv[1])
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    res_dir = os.path.join(base, "resultados")
    os.makedirs(res_dir, exist_ok=True)
    pomar = gerar_pomar(mat)
    n = len(pomar)
    with open(os.path.join(res_dir, "pomar.txt"), "w", encoding="utf-8") as f:
        f.write(f"{mat}\n")
        for linha in pomar:
            f.write(" ".join(linha) + "\n")
    objetivo = (n - 1, n - 1)
    resultados = []
    testes = [
        ("BFS", "", lambda: bfs(pomar, objetivo=objetivo)),
        ("DFS", "", lambda: dfs(pomar, objetivo=objetivo)),
        ("UCS", "", lambda: ucs(pomar, objetivo=objetivo)),
        ("A*", "h1=0", lambda: a_estrela(pomar, h1_zero, objetivo=objetivo)),
        ("A*", "h2=Manhattan", lambda: a_estrela(pomar, h2_manhattan, objetivo=objetivo)),
        ("A*", "h3=4xManhattan", lambda: a_estrela(pomar, h3_ponderada, objetivo=objetivo)),
    ]
    for est, heu, fn in testes:
        r, dt = medir(fn)
        resultados.append({"estrategia": est, "heuristica": heu, "custo": r["custo"],
                           "passos": r["passos"], "nos_expandidos": r["nos_expandidos"],
                           "fronteira_max": r["fronteira_max"], "tempo_ms": round(dt, 2)})
        print(f"{est} [{heu}]: custo={r['custo']} passos={r['passos']} "
              f"expandidos={r['nos_expandidos']} front_max={r['fronteira_max']} {dt:.1f}ms")
    with open(os.path.join(res_dir, "resultados.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["estrategia", "heuristica", "custo", "passos",
                                          "nos_expandidos", "fronteira_max", "tempo_ms"])
        w.writeheader()
        w.writerows(resultados)
    salvar_grafico(resultados, os.path.join(res_dir, "grafico.png"))
    livres = [(i, j) for i in range(n) for j in range(n) if pomar[i][j] != "#"]
    valores = gerar_valores(livres, mat)
    exp = rodar_30vezes(livres, valores, seed_base=mat % 100000)
    print(f"Busca local K=15: hill media={exp['hill']['media']:.2f} "
          f"dp={exp['hill']['desvio']:.2f} melhor={exp['hill']['melhor']:.2f} | "
          f"SA media={exp['sa']['media']:.2f} dp={exp['sa']['desvio']:.2f} "
          f"melhor={exp['sa']['melhor']:.2f}")
    print("Sensor:", parametros_sensor(mat))
    print("OK: resultados.csv, grafico.png, pomar.txt gerados em resultados/")


if __name__ == "__main__":
    main()
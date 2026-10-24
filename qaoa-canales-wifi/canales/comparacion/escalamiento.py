from ..clasico.metodos import resolver_fuerza_bruta
from ..config import QAOA
from ..cuantico.qaoa import resolver_qaoa
from .metricas import prob_optimo
from ..modelo.red import red_aleatoria

TAMANOS = (4, 5, 6, 7)
SEMILLAS = (0, 1)
CAPAS = (1, 2)


def barrido(tamanos=TAMANOS, semillas=SEMILLAS, capas=CAPAS):
    filas = []
    for n in tamanos:
        for semilla in semillas:
            red = red_aleatoria(n, semilla)
            fb = resolver_fuerza_bruta(red)
            for reps in capas:
                q = resolver_qaoa(red, dict(QAOA, REPS=reps, SEMILLA=semilla))
                filas.append({
                    "n": n,
                    "semilla": semilla,
                    "reps": reps,
                    "optimo": fb["costo"],
                    "p_optimo": round(prob_optimo(red, q, fb["costo"]), 4),
                    "acierta_mas_probable": q["extra"]["costo_mas_probable"] == fb["costo"],
                    "tiempo_qaoa_s": round(q["tiempo_s"], 3),
                    "tiempo_fuerza_bruta_s": round(fb["tiempo_s"], 6),
                    "profundidad": q["extra"]["profundidad"],
                })
    return filas

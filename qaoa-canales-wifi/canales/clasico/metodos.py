import itertools
import time

import numpy as np

from ..config import CLASICO
from ..modelo.hamiltoniano import interferencia


def _resultado(nombre, x, red, t0):
    return {
        "metodo": nombre,
        "x": [int(v) for v in x],
        "costo": interferencia(red, x),
        "tiempo_s": time.perf_counter() - t0,
        "extra": {},
    }


def resolver_fuerza_bruta(red, params=CLASICO):
    if red["n"] > params["MAX_ANTENAS_FUERZA_BRUTA"]:
        raise ValueError("Demasiadas antenas para fuerza bruta")
    t0 = time.perf_counter()
    mejor = min(itertools.product([0, 1], repeat=red["n"]), key=lambda x: interferencia(red, x))
    return _resultado("Fuerza bruta", mejor, red, t0)


def resolver_voraz(red, params=CLASICO):
    t0 = time.perf_counter()
    n = red["n"]
    molestia = [sum(w for i, j, w in red["interf"] if v in (i, j)) for v in range(n)]
    x = [None] * n
    for v in sorted(range(n), key=lambda v: -molestia[v]):
        choque = [
            sum(w for i, j, w in red["interf"] if (i == v and x[j] == c) or (j == v and x[i] == c))
            for c in (0, 1)
        ]
        x[v] = int(np.argmin(choque))
    return _resultado("Voraz", x, red, t0)


def resolver_busqueda_local(red, params=CLASICO):
    t0 = time.perf_counter()
    rng = np.random.default_rng(params["SEMILLA"])
    mejor_x, mejor_c = None, float("inf")
    for _ in range(params["REINICIOS"]):
        x = [int(v) for v in rng.integers(0, 2, red["n"])]
        c = interferencia(red, x)
        mejora = True
        while mejora:
            mejora = False
            for v in range(red["n"]):
                x[v] ^= 1
                c2 = interferencia(red, x)
                if c2 < c:
                    c, mejora = c2, True
                else:
                    x[v] ^= 1
        if c < mejor_c:
            mejor_x, mejor_c = x[:], c
    return _resultado("Busqueda local", mejor_x, red, t0)


def resolver_clasicos(red, params=CLASICO):
    return [resolver_fuerza_bruta(red, params), resolver_voraz(red, params), resolver_busqueda_local(red, params)]

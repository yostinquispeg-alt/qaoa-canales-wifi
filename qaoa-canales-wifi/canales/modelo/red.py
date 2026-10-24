import math

import numpy as np

from ..config import RED


def construir_red(nombre, posiciones, origen, destino, params=RED):
    n = len(posiciones)
    interf, com = [], []
    for i in range(n):
        for j in range(i + 1, n):
            d = math.dist(posiciones[i], posiciones[j])
            if d < params["RADIO_INTERFERENCIA"]:
                peso = params["PESO_MAXIMO"] * (1 - d / params["RADIO_INTERFERENCIA"])
                interf.append((i, j, round(peso, 2)))
            if d < params["RADIO_COMUNICACION"]:
                com.append((i, j, round(params["COSTO_POR_METRO"] * d, 2)))
    red = {
        "nombre": nombre,
        "n": n,
        "pos": [list(p) for p in posiciones],
        "interf": interf,
        "com": com,
        "origen": origen,
        "destino": destino,
    }
    validar_red(red)
    return red


def red_aleatoria(n, semilla=0, lado=8.0, params=RED):
    rng = np.random.default_rng(semilla)
    posiciones = [tuple(p) for p in rng.uniform(0, lado, size=(n, 2)).round(2)]
    return construir_red(f"aleatoria_{n}_{semilla}", posiciones, 0, n - 1, params)


def validar_red(red):
    n = red["n"]
    if len(red["pos"]) != n:
        raise ValueError("Se requiere una posicion por antena")
    for clave in ("interf", "com"):
        for i, j, peso in red[clave]:
            if not (0 <= i < n and 0 <= j < n) or i == j:
                raise ValueError(f"Arista invalida en '{clave}': {(i, j)}")
            if peso < 0:
                raise ValueError(f"Peso negativo en '{clave}': {(i, j, peso)}")
    if not (0 <= red["origen"] < n and 0 <= red["destino"] < n):
        raise ValueError("Origen o destino fuera de rango")
    return True

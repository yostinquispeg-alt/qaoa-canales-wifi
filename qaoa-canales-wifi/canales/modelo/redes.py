from .red import construir_red, validar_red


def pasillo():
    posiciones = [(0, 0), (3, 0), (6, 0), (0, 3), (3, 3), (6, 3)]
    return construir_red("pasillo", posiciones, origen=0, destino=5)


def triangulos():
    red = {
        "nombre": "triangulos",
        "n": 5,
        "pos": [[0, 2], [2, 2], [0, 0.6], [2, 0.6], [1, -0.6]],
        "interf": [(0, 1, 3.0), (0, 2, 1.0), (1, 2, 2.0), (1, 3, 1.5), (2, 4, 2.5), (3, 4, 1.0), (0, 4, 0.5)],
        "com": [(0, 1, 1.0), (1, 2, 1.0), (0, 2, 2.5), (1, 3, 1.0), (2, 4, 1.0), (3, 4, 1.5)],
        "origen": 0,
        "destino": 4,
    }
    validar_red(red)
    return red


REDES = {"triangulos": triangulos, "pasillo": pasillo}

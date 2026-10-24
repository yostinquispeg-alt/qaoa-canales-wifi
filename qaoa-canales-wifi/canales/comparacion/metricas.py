from ..config import RUTAS
from ..modelo.hamiltoniano import interferencia
from ..clasico.rutas import mejor_ruta


def prob_optimo(red, res_qaoa, costo_optimo, tol=1e-9):
    return sum(p for x, p in res_qaoa["extra"]["muestras"] if abs(interferencia(red, x) - costo_optimo) < tol)


def tabla_comparativa(red, resultados, params_rutas=RUTAS):
    optimo = next(r["costo"] for r in resultados if r["metodo"] == "Fuerza bruta")
    filas = []
    for r in resultados:
        ruta = mejor_ruta(red, r["x"], params_rutas)
        fila = {
            "Metodo": r["metodo"],
            "Interferencia": r["costo"],
            "Distancia al optimo": round(r["costo"] - optimo, 4),
            "Ruta": "-".join(map(str, ruta["camino"])),
            "Costo ruta": round(ruta["costo"], 2),
            "Tiempo (s)": round(r["tiempo_s"], 4),
        }
        if r["metodo"] == "QAOA":
            fila["P(optimo)"] = round(prob_optimo(red, r, optimo), 3)
            fila["Interf. mas probable"] = r["extra"]["costo_mas_probable"]
        filas.append(fila)
    return filas

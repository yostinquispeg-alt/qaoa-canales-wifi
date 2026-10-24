import argparse
import itertools
import os
import warnings

import matplotlib.pyplot as plt
import numpy as np
from scipy.sparse import SparseEfficiencyWarning

from canales.clasico.metodos import resolver_clasicos
from canales.clasico.rutas import mejor_ruta
from canales.comparacion import graficas as G
from canales.comparacion.escalamiento import barrido
from canales.comparacion.metricas import tabla_comparativa
from canales.cuantico.qaoa import resolver_qaoa
from canales.modelo.hamiltoniano import hamiltoniano, interferencia, interferencia_total_posible
from canales.modelo.redes import REDES

warnings.filterwarnings("ignore", category=SparseEfficiencyWarning)


def titulo(n, texto):
    print(f"\n{'=' * 70}\n {n}. {texto}\n{'=' * 70}")


def tabla(filas):
    columnas = list(dict.fromkeys(k for f in filas for k in f))
    anchos = {c: max(len(c), *(len(str(f.get(c, ""))) for f in filas)) for c in columnas}
    print(" | ".join(c.ljust(anchos[c]) for c in columnas))
    print("-+-".join("-" * anchos[c] for c in columnas))
    for f in filas:
        print(" | ".join(str(f.get(c, "")).ljust(anchos[c]) for c in columnas))


class Salida:
    def __init__(self, carpeta, red):
        self.carpeta, self.red = carpeta, red

    def mostrar(self, fig, nombre):
        if self.carpeta:
            os.makedirs(self.carpeta, exist_ok=True)
            ruta = os.path.join(self.carpeta, f"{nombre}_{self.red}.png" if self.red else f"{nombre}.png")
            fig.savefig(ruta, dpi=110, bbox_inches="tight")
            plt.close(fig)
            print(f"   figura guardada: {ruta}")


def demo(nombre, carpeta=None):
    red = REDES[nombre]()
    salida = Salida(carpeta, nombre)

    titulo(1, f"EL PROBLEMA: red '{nombre}' con {red['n']} antenas y 2 canales")
    W = interferencia_total_posible(red)
    print(f"   Parejas que se interfieren: {len(red['interf'])}")
    print(f"   Interferencia si todas usan el mismo canal: {W:.2f}")
    print(f"   Ruta de los datos: antena {red['origen']} -> antena {red['destino']}")
    fig, ax = plt.subplots(figsize=(6, 4.5))
    G.dibujar_red(red, [0] * red["n"], "Situación inicial: todas en el canal 0", ax)
    G.leyenda_red(fig)
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    salida.mostrar(fig, "red_inicial")

    titulo(2, "EL MODELO CUÁNTICO: 1 antena = 1 qubit (modelo de Ising)")
    problema, H, _ = hamiltoniano(red)
    error = max(
        abs(interferencia(red, x) - (W - problema.objective.evaluate(np.array(x))))
        for x in itertools.product([0, 1], repeat=red["n"])
    )
    print(f"   Qubits: {H.num_qubits} | términos del hamiltoniano: {len(H)}")
    print(f"   Verificación interferencia = W - corte en las {2 ** red['n']} asignaciones: error {error:.1e}")

    titulo(3, "SOLUCIÓN CUÁNTICO-HÍBRIDA: QAOA")
    q = resolver_qaoa(red)
    e = q["extra"]
    print(f"   Capas: {e['parametros']['REPS']} | evaluaciones del optimizador: {e['evaluaciones']} | tiempo: {q['tiempo_s']:.1f} s")
    print(f"   Resultado más probable: {e['x_mas_probable']} -> interferencia {e['costo_mas_probable']:.2f}")
    print(f"   Mejor medición:         {q['x']} -> interferencia {q['costo']:.2f}")

    titulo(4, "SOLUCIONES CLÁSICAS Y RUTAS")
    clasicos = resolver_clasicos(red)
    for r in clasicos:
        ruta = mejor_ruta(red, r["x"])
        print(f"   {r['metodo']:15s} interferencia {r['costo']:.2f} | ruta {'-'.join(map(str, ruta['camino']))} (costo {ruta['costo']:.2f}) | {r['tiempo_s'] * 1e3:.3f} ms")
    sin = mejor_ruta(red, [0] * red["n"])
    print(f"   {'Sin optimizar':15s} interferencia {W:.2f} | ruta {'-'.join(map(str, sin['camino']))} (costo {sin['costo']:.2f})")

    titulo(5, "COMPARACIÓN")
    resultados = clasicos + [q]
    filas = tabla_comparativa(red, resultados)
    tabla(filas)
    fig = G.armar_display(red, resultados, filas)
    salida.mostrar(fig, "display")

    titulo(6, "CONCLUSIÓN")
    optimo = clasicos[0]["costo"]
    fila_q = next(f for f in filas if f["Metodo"] == "QAOA")
    azar = 2 / 2 ** red["n"]
    acierta = e["costo_mas_probable"] == optimo
    veces = q["tiempo_s"] / max(clasicos[0]["tiempo_s"], 1e-9)
    print(f"   Óptimo exacto: {optimo:.2f} (frente a {W:.2f} sin optimizar)")
    print(f"   QAOA mide el óptimo el {fila_q['P(optimo)']:.1%} de las veces; al azar sería {azar:.1%} -> {fila_q['P(optimo)'] / azar:.1f} veces más")
    print(f"   El resultado más probable de QAOA {'SÍ' if acierta else 'NO'} es el óptimo")
    print(f"   La ruta de los datos baja de {sin['costo']:.2f} a {mejor_ruta(red, clasicos[0]['x'])['costo']:.2f} con la asignación óptima")
    print(f"   A este tamaño la fuerza bruta es ~{veces:,.0f} veces más rápida que QAOA en simulador")
    print("   QAOA encuentra buenas soluciones mucho más seguido que el azar, pero no supera a lo clásico en problemas pequeños.")


def escalamiento(carpeta=None):
    titulo(7, "ESCALAMIENTO: redes aleatorias de 4 a 7 antenas")
    filas = barrido()
    tabla(filas)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4))
    G.escalamiento(filas, ax[0], ax[1])
    fig.tight_layout()
    Salida(carpeta, None).mostrar(fig, "escalamiento")


def main():
    parser = argparse.ArgumentParser(description="Asignacion de canales Wi-Fi: clasico vs QAOA")
    parser.add_argument("red", nargs="?", default="triangulos", choices=list(REDES) + ["todas"])
    parser.add_argument("--escalamiento", action="store_true")
    parser.add_argument("--guardar", metavar="CARPETA")
    args = parser.parse_args()

    for nombre in (list(REDES) if args.red == "todas" else [args.red]):
        demo(nombre, args.guardar)
    if args.escalamiento:
        escalamiento(args.guardar)
    if not args.guardar:
        print("\nAbriendo las figuras...")
        plt.show()


if __name__ == "__main__":
    main()

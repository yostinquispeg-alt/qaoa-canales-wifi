import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from ..config import ESTILO, RUTAS
from ..modelo.hamiltoniano import interferencia
from ..clasico.rutas import mejor_ruta

CANAL = {0: "#2a78d6", 1: "#eb6834"}
METODO = {"Voraz": "#1baf7a", "Busqueda local": "#1baf7a", "QAOA": "#6250d6"}
TEXTO, TEXTO_2, GRILLA, FONDO = "#0b0b0b", "#52514e", "#e6e5e1", "#fcfcfb"
CONFLICTO = "#e34948"
SIN_CONFLICTO = "#c9c8c2"
RUTA = "#008300"


def aplicar_estilo():
    mpl.rcParams.update({
        "figure.facecolor": FONDO, "axes.facecolor": FONDO, "savefig.facecolor": FONDO,
        "axes.edgecolor": GRILLA, "axes.labelcolor": TEXTO_2, "axes.titlecolor": TEXTO,
        "axes.titleweight": "bold", "axes.titlesize": 12, "font.size": 10,
        "xtick.color": TEXTO_2, "ytick.color": TEXTO_2, "axes.grid": True,
        "grid.color": GRILLA, "grid.linewidth": 0.8, "axes.spines.top": False,
        "axes.spines.right": False, "legend.frameon": False, "figure.dpi": 110,
    })


aplicar_estilo()


def dibujar_red(red, x, titulo, ax, mostrar_ruta=True, params_rutas=RUTAS):
    pos = red["pos"]
    for i, j, w in red["interf"]:
        activa = x[i] == x[j]
        ax.plot(
            [pos[i][0], pos[j][0]], [pos[i][1], pos[j][1]],
            color=CONFLICTO if activa else SIN_CONFLICTO,
            lw=1 + 0.8 * w, ls="-" if activa else "--", zorder=1,
        )
    if mostrar_ruta:
        camino = mejor_ruta(red, x, params_rutas)["camino"]
        for a, b in zip(camino, camino[1:]):
            ax.annotate(
                "", xy=pos[b], xytext=pos[a], zorder=2,
                arrowprops=dict(arrowstyle="-|>", color=RUTA, lw=2.5, shrinkA=13, shrinkB=13),
            )
    for v, (px, py) in enumerate(pos):
        ax.scatter(px, py, s=ESTILO["TAMANO_ANTENA"], color=CANAL[x[v]], edgecolors=FONDO, linewidths=2, zorder=3)
        ax.text(px, py, str(v), ha="center", va="center", color="white", fontweight="bold", zorder=4)
    ax.set_title(titulo)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.margins(0.18)


def leyenda_red(fig):
    h = [
        Line2D([], [], marker="o", ls="", ms=11, color=CANAL[0], label="Canal 0"),
        Line2D([], [], marker="o", ls="", ms=11, color=CANAL[1], label="Canal 1"),
        Line2D([], [], color=CONFLICTO, lw=2.5, label="Interfieren (mismo canal)"),
        Line2D([], [], color=SIN_CONFLICTO, lw=2, ls="--", label="Sin interferencia"),
        Line2D([], [], color=RUTA, lw=2.5, label="Ruta de los datos"),
    ]
    fig.legend(handles=h, loc="lower center", ncol=5, fontsize=9)


def barras_metodos(filas, ax):
    opt = next(f["Interferencia"] for f in filas if f["Metodo"] == "Fuerza bruta")
    datos = []
    for f in filas:
        if f["Metodo"] == "Voraz":
            datos.append(("Voraz", f["Interferencia"], METODO["Voraz"]))
        elif f["Metodo"] == "Busqueda local":
            datos.append(("Búsqueda\nlocal", f["Interferencia"], METODO["Busqueda local"]))
        elif f["Metodo"] == "QAOA":
            datos.append(("QAOA\nprobable", f["Interf. mas probable"], METODO["QAOA"]))
            datos.append(("QAOA\nmejor", f["Interferencia"], METODO["QAOA"]))
    nombres, valores, colores = zip(*datos)
    barras = ax.bar(nombres, valores, color=colores, width=0.55, zorder=2)
    ax.bar_label(barras, fmt="%.2f", color=TEXTO, padding=3)
    ax.axhline(opt, color=TEXTO, ls=":", lw=1.5, zorder=3, label=f"Óptimo exacto = {opt:.2f}")
    ax.set_ylim(0, max(valores) * 1.35 + 0.1)
    ax.legend(loc="upper left", fontsize=9)
    ax.set_ylabel("Interferencia (menos es mejor)")
    ax.set_title("Interferencia por método")
    ax.grid(axis="x", visible=False)


def histograma_qaoa(red, res_qaoa, costo_optimo, ax, top=None):
    top = top or ESTILO["TOP_HISTOGRAMA"]
    muestras = sorted(res_qaoa["extra"]["muestras"], key=lambda m: -m[1])[:top]
    etiquetas = ["".join(map(str, x)) for x, _ in muestras]
    probs = [p for _, p in muestras]
    colores = [
        METODO["QAOA"] if abs(interferencia(red, x) - costo_optimo) < 1e-9 else SIN_CONFLICTO
        for x, _ in muestras
    ]
    ax.bar(etiquetas, probs, color=colores, zorder=2)
    ax.set_ylabel("Probabilidad")
    ax.set_xlabel("Canales (antena 0 … n-1)")
    ax.set_title("Mediciones de QAOA (morado = óptimo)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(axis="x", visible=False)


def convergencia(res_qaoa, ax):
    h = res_qaoa["extra"]["historial"]
    ax.plot(range(1, len(h) + 1), h, color=METODO["QAOA"], lw=2)
    ax.set_xlabel("Iteración del optimizador clásico")
    ax.set_ylabel("Energía")
    ax.set_title("Convergencia del optimizador")


def escalamiento(filas, ax_p, ax_t=None):
    tonos = ["#9085e9", "#6250d6", "#3a2a9e"]
    tamanos = sorted({f["n"] for f in filas})
    capas = sorted({f["reps"] for f in filas})

    def promedio(clave, n, reps):
        v = [float(f[clave]) for f in filas if f["n"] == n and f["reps"] == reps]
        return sum(v) / len(v)

    for k, reps in enumerate(capas):
        c = tonos[k % len(tonos)]
        ax_p.plot(tamanos, [promedio("p_optimo", n, reps) for n in tamanos], marker="o", color=c, lw=2, label=f"QAOA reps = {reps}")
        if ax_t is not None:
            ax_t.plot(tamanos, [promedio("tiempo_qaoa_s", n, reps) for n in tamanos], marker="o", color=c, lw=2, label=f"QAOA reps = {reps}")
    ax_p.plot(tamanos, [2 / 2 ** n for n in tamanos], ls=":", color=TEXTO_2, label="Elegir al azar")
    ax_p.set(xlabel="Antenas (= qubits)", ylabel="P(óptimo)", title="Frecuencia con que QAOA mide el óptimo")
    ax_p.set_xticks(tamanos)
    ax_p.legend(fontsize=9)
    if ax_t is not None:
        ax_t.plot(tamanos, [promedio("tiempo_fuerza_bruta_s", n, capas[0]) for n in tamanos], ls=":", color=TEXTO_2, label="Fuerza bruta")
        ax_t.set(xlabel="Antenas (= qubits)", ylabel="Segundos", title="Tiempo de cómputo (simulador local)")
        ax_t.set_yscale("log")
        ax_t.set_xticks(tamanos)
        ax_t.legend(fontsize=9)


def armar_tablero(red, resultados, filas, params_rutas=RUTAS):
    por_metodo = {r["metodo"]: r for r in resultados}
    fb, vor, q = por_metodo["Fuerza bruta"], por_metodo["Voraz"], por_metodo["QAOA"]
    fig = plt.figure(figsize=ESTILO["TAMANO_TABLERO"])
    gs = fig.add_gridspec(2, 3, height_ratios=[1.15, 1])
    dibujar_red(red, fb["x"], "Óptimo (fuerza bruta)", fig.add_subplot(gs[0, 0]), params_rutas=params_rutas)
    dibujar_red(red, vor["x"], "Clásico rápido (voraz)", fig.add_subplot(gs[0, 1]), params_rutas=params_rutas)
    dibujar_red(red, q["extra"]["x_mas_probable"], "QAOA (resultado más probable)", fig.add_subplot(gs[0, 2]), params_rutas=params_rutas)
    barras_metodos(filas, fig.add_subplot(gs[1, 0]))
    histograma_qaoa(red, q, fb["costo"], fig.add_subplot(gs[1, 1]))
    convergencia(q, fig.add_subplot(gs[1, 2]))
    fig.suptitle(f"Asignación de canales y rutas — red '{red['nombre']}'", fontsize=15, fontweight="bold")
    leyenda_red(fig)
    fig.tight_layout(rect=(0, 0.05, 1, 0.96))
    return fig


def costo_rutas(red, filas, ax, params_rutas=RUTAS):
    etiquetas = {"Fuerza bruta": "Óptimo", "Voraz": "Voraz", "Busqueda local": "Búsqueda\nlocal", "QAOA": "QAOA\nmejor"}
    colores = {"Fuerza bruta": TEXTO_2, "Voraz": METODO["Voraz"], "Busqueda local": METODO["Voraz"], "QAOA": METODO["QAOA"]}
    nombres = ["Sin\noptimizar"] + [etiquetas[f["Metodo"]] for f in filas]
    valores = [mejor_ruta(red, [0] * red["n"], params_rutas)["costo"]] + [f["Costo ruta"] for f in filas]
    barras = ax.bar(nombres, valores, color=[SIN_CONFLICTO] + [colores[f["Metodo"]] for f in filas], width=0.55, zorder=2)
    ax.bar_label(barras, fmt="%.2f", color=TEXTO, padding=3)
    ax.set_ylim(0, max(valores) * 1.3)
    ax.set_ylabel("Costo de la ruta (menos es mejor)")
    ax.set_title("Ruta de los datos según la asignación")
    ax.grid(axis="x", visible=False)


def armar_display(red, resultados, filas, params_rutas=RUTAS):
    por_metodo = {r["metodo"]: r for r in resultados}
    fb, vor, q = por_metodo["Fuerza bruta"], por_metodo["Voraz"], por_metodo["QAOA"]
    fila_q = next(f for f in filas if f["Metodo"] == "QAOA")
    azar = 2 / 2 ** red["n"]

    fig = plt.figure(figsize=(18, 14))
    gs = fig.add_gridspec(3, 3, height_ratios=[1.1, 1.1, 1])
    dibujar_red(red, [0] * red["n"], "1 · Red: todas en el canal 0", fig.add_subplot(gs[0, 0]), params_rutas=params_rutas)
    dibujar_red(red, fb["x"], "2 · Óptimo exacto (fuerza bruta)", fig.add_subplot(gs[0, 1]), params_rutas=params_rutas)
    dibujar_red(red, q["extra"]["x_mas_probable"], "3 · QAOA: resultado más probable", fig.add_subplot(gs[0, 2]), params_rutas=params_rutas)
    dibujar_red(red, vor["x"], "4 · Clásico rápido (voraz)", fig.add_subplot(gs[1, 0]), params_rutas=params_rutas)
    histograma_qaoa(red, q, fb["costo"], fig.add_subplot(gs[1, 1]))
    convergencia(q, fig.add_subplot(gs[1, 2]))
    barras_metodos(filas, fig.add_subplot(gs[2, 0]))
    costo_rutas(red, filas, fig.add_subplot(gs[2, 1]), params_rutas)
    ax_r = fig.add_subplot(gs[2, 2])
    ax_r.axis("off")
    resumen = [
        ("Antenas = qubits", f"{red['n']}"),
        ("Interferencia sin optimizar", f"{sum(w for _, _, w in red['interf']):.2f}"),
        ("Óptimo exacto", f"{fb['costo']:.2f}"),
        ("Voraz", f"{vor['costo']:.2f}"),
        ("QAOA más probable", f"{fila_q['Interf. mas probable']:.2f}"),
        ("P(óptimo) QAOA", f"{fila_q['P(optimo)']:.1%}"),
        ("P(óptimo) al azar", f"{azar:.1%}"),
        ("Ruta óptima", f"{next(f['Ruta'] for f in filas if f['Metodo'] == 'Fuerza bruta')}"),
        ("Tiempo fuerza bruta", f"{fb['tiempo_s'] * 1e3:.2f} ms"),
        ("Tiempo QAOA (simulador)", f"{q['tiempo_s']:.1f} s"),
    ]
    ax_r.set_title("Resumen")
    for k, (etiqueta, valor) in enumerate(resumen):
        y = 0.93 - k * 0.095
        ax_r.text(0.02, y, etiqueta, color=TEXTO_2, fontsize=11, transform=ax_r.transAxes)
        ax_r.text(0.98, y, valor, color=TEXTO, fontsize=11, fontweight="bold", ha="right", transform=ax_r.transAxes)
    fig.suptitle(
        f"Asignación de canales Wi-Fi: clásico vs QAOA — red '{red['nombre']}'",
        fontsize=17, fontweight="bold",
    )
    leyenda_red(fig)
    fig.tight_layout(rect=(0, 0.04, 1, 0.97))
    return fig

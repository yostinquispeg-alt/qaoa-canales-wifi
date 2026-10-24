import rustworkx as rx

from ..config import RUTAS


def interferencia_en_antena(red, x, v):
    return sum(
        w for i, j, w in red["interf"] if (i == v and x[j] == x[v]) or (j == v and x[i] == x[v])
    )


def costo_enlaces(red, x, params=RUTAS):
    return [
        (i, j, d + params["ALPHA"] * (interferencia_en_antena(red, x, i) + interferencia_en_antena(red, x, j)))
        for i, j, d in red["com"]
    ]


def mejor_ruta(red, x, params=RUTAS):
    s, t = red["origen"], red["destino"]
    g = rx.PyGraph()
    g.add_nodes_from(range(red["n"]))
    g.add_edges_from(costo_enlaces(red, x, params))
    caminos = rx.dijkstra_shortest_paths(g, s, target=t, weight_fn=float)
    if t not in caminos:
        return {"camino": [], "costo": float("inf")}
    largos = rx.dijkstra_shortest_path_lengths(g, s, edge_cost_fn=float, goal=t)
    return {"camino": list(caminos[t]), "costo": round(float(largos[t]), 4)}

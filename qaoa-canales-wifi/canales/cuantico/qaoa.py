import time

import numpy as np
from qiskit.circuit.library import QAOAAnsatz
from qiskit.primitives import StatevectorEstimator, StatevectorSampler
from scipy.optimize import minimize

from ..config import QAOA
from ..modelo.hamiltoniano import hamiltoniano, interferencia


def bits_a_canales(bitstring):
    return [int(b) for b in reversed(bitstring)]


def resolver_qaoa(red, params=QAOA):
    t0 = time.perf_counter()
    _, H, _ = hamiltoniano(red)
    ansatz = QAOAAnsatz(cost_operator=H, reps=params["REPS"])
    estimator = StatevectorEstimator()
    historial = []

    def energia(angulos):
        ev = float(estimator.run([(ansatz, H, angulos)]).result()[0].data.evs)
        historial.append(ev)
        return ev

    rng = np.random.default_rng(params["SEMILLA"])
    inicio = rng.uniform(0, np.pi, ansatz.num_parameters)
    opt = minimize(
        energia,
        inicio,
        method=params["OPTIMIZADOR"],
        tol=1e-3,
        options={"maxiter": params["MAX_ITER"]},
    )

    circuito = ansatz.assign_parameters(opt.x)
    circuito.measure_all()
    sampler = StatevectorSampler(seed=params["SEMILLA"])
    counts = sampler.run([circuito], shots=params["SHOTS"]).result()[0].data.meas.get_counts()

    muestras = [(bits_a_canales(b), c / params["SHOTS"]) for b, c in counts.items()]
    x_probable = max(muestras, key=lambda m: m[1])[0]
    x_mejor = min(muestras, key=lambda m: interferencia(red, m[0]))[0]
    return {
        "metodo": "QAOA",
        "x": x_mejor,
        "costo": interferencia(red, x_mejor),
        "tiempo_s": time.perf_counter() - t0,
        "extra": {
            "x_mas_probable": x_probable,
            "costo_mas_probable": interferencia(red, x_probable),
            "muestras": muestras,
            "historial": historial,
            "qubits": H.num_qubits,
            "profundidad": ansatz.decompose().depth(),
            "evaluaciones": len(historial),
            "parametros": dict(params),
        },
    }

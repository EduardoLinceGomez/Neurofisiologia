"""Tres balances de corriente pasivos, con solución mediante solve_ivp."""

from dataclasses import dataclass

import numpy as np
from scipy.integrate import solve_ivp

from .parameters import RodParameters
from .stimulus import PhotonEvents


def conductance_matrix(parameters: RodParameters) -> np.ndarray:
    """K simétrica: balance oscuro = -K V + gL E, en pA."""
    goi, git = parameters.g_oi_ns, parameters.g_it_ns
    return np.diag(parameters.leak_ns) + np.array([
        [goi, -goi, 0.0],
        [-goi, goi + git, -git],
        [0.0, -git, git],
    ])


def dark_equilibrium(parameters: RodParameters = RodParameters()) -> np.ndarray:
    """Resuelve K V = gL E; si todos los E=-40, todos los V=-40 mV."""
    return np.linalg.solve(conductance_matrix(parameters),
                           np.asarray(parameters.leak_ns) * parameters.reversal_mv)


def current_balance(t_ms: float, voltage_mv, parameters: RodParameters,
                    stimulus: PhotonEvents) -> np.ndarray:
    """Corriente neta entrante (pA) en O, I, T; axiales iguales y opuestas."""
    voltage = np.asarray(voltage_mv, dtype=float)
    if voltage.shape != (3,) or not np.all(np.isfinite(voltage)):
        raise ValueError("voltage_mv debe tener tres valores finitos (O, I, T)")
    net = -np.asarray(parameters.leak_ns) * (voltage - parameters.reversal_mv)
    i_oi = parameters.g_oi_ns * (voltage[1] - voltage[0])
    i_it = parameters.g_it_ns * (voltage[2] - voltage[1])
    net += np.array([i_oi, -i_oi + i_it, -i_it])
    net[0] += stimulus.current(t_ms)
    return net


def rhs(t_ms: float, voltage_mv, parameters: RodParameters,
        stimulus: PhotonEvents) -> np.ndarray:
    """dV/dt en mV/ms: pA/pF = mV/ms."""
    return current_balance(t_ms, voltage_mv, parameters, stimulus) / parameters.capacitance_pf


@dataclass(frozen=True)
class SimulationResult:
    """Salida muestreada: voltage_mv tiene forma (3, número de tiempos)."""

    time_ms: np.ndarray
    voltage_mv: np.ndarray
    photocurrent_pa: np.ndarray
    parameters: RodParameters
    stimulus: PhotonEvents


def simulate(time_ms, parameters: RodParameters = RodParameters(),
             stimulus: PhotonEvents = PhotonEvents(), *, initial_voltage_mv=None,
             rtol: float = 1e-8, atol: float = 1e-10,
             max_step_ms: float | None = None) -> SimulationResult:
    """Integra sobre el intervalo de `time_ms`, desde el equilibrio por defecto.

    Los eventos previos al inicio aún contribuyen a la corriente, pero el estado
    inicial no reconstruye su historia: iniciar antes del primer evento, o pasar
    un estado inicial ya calculado. La malla de salida no es el paso adaptativo.
    Se limita el paso interno a t_peak/30 para no saltar una respuesta tardía
    o breve; max_step_ms puede hacerlo aún menor. No se trunca la cola de h.
    Se integra V-V_oscuro para controlar el error sobre la respuesta pequeña,
    en vez de aplicar la tolerancia relativa al desplazamiento de -40 mV.
    """
    times = np.asarray(time_ms, dtype=float)
    if (times.ndim != 1 or times.size < 2 or not np.all(np.isfinite(times))
            or np.any(np.diff(times) <= 0)):
        raise ValueError("time_ms debe ser un vector finito estrictamente creciente")
    for name, value in (("rtol", rtol), ("atol", atol)):
        if not np.isfinite(value) or value <= 0:
            raise ValueError(f"{name} debe ser finito y positivo")
    if max_step_ms is not None and (not np.isfinite(max_step_ms) or max_step_ms <= 0):
        raise ValueError("max_step_ms debe ser finito y positivo")
    initial = (dark_equilibrium(parameters) if initial_voltage_mv is None
               else np.asarray(initial_voltage_mv, dtype=float))
    if initial.shape != (3,) or not np.all(np.isfinite(initial)):
        raise ValueError("initial_voltage_mv debe tener tres valores finitos")
    step = stimulus.t_peak_ms / 30
    if max_step_ms is not None:
        step = min(step, max_step_ms)
    equilibrium = dark_equilibrium(parameters)
    capacitance = np.asarray(parameters.capacitance_pf)
    matrix = conductance_matrix(parameters)

    def deviation_rhs(t, deviation):
        net = -matrix @ deviation
        net[0] += stimulus.current(t)
        return net / capacitance

    solution = solve_ivp(
        deviation_rhs, (times[0], times[-1]), initial-equilibrium, t_eval=times,
        method="RK45", rtol=rtol, atol=atol,
        max_step=step,
    )
    if not solution.success:
        raise RuntimeError(f"solve_ivp no completó la integración: {solution.message}")
    if solution.y.shape != (3, times.size) or not np.all(np.isfinite(solution.y)):
        raise RuntimeError("solve_ivp devolvió una solución incompleta o no finita")
    return SimulationResult(times.copy(), equilibrium[:, None]+solution.y, stimulus.current(times),
                            parameters, stimulus)

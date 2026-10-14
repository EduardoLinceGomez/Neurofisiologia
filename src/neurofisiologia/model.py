"""Tres balances de corriente pasivos, con solución mediante solve_ivp."""

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
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
    """V_dark (mV), forma (3,), orden O,I,T, resuelve K V=gL E.

    g y K tienen nS; E tiene mV. La fuga positiva asegura solución única.
    E distintos no permiten suponer V=E; E iguales dan ese mismo reposo.
    Es equilibrio del circuito ilustrativo, no medición del bastón real.
    """
    return np.linalg.solve(conductance_matrix(parameters),
                           np.asarray(parameters.leak_ns) * parameters.reversal_mv)


def decompose_currents(t_ms: float | ArrayLike, voltage_mv: ArrayLike,
                       parameters: RodParameters,
                       stimulus: PhotonEvents) -> dict[str, NDArray[np.float64]]:
    """Desglosa las corrientes impuestas, de fuga y axiales en pA.

    Para un instante (ms), V (mV) tiene forma (3,); para n instantes, (3,n).
    Orden O,I,T. leak_current_pa=-gL*(V-E); photocurrent_pa contiene la
    entrada solo en O; axial_current_pa suma entradas axiales por nodo.
    axial_current_oi_pa=gOI*(VO-VI) es positiva O→I, y
    axial_current_it_pa=gIT*(VI-VT) es positiva I→T; tienen forma () o (n,).
    Las contribuciones por nodo son (-Ioi, Ioi-Iit, Iit): su suma es cero.
    net_current_pa=leak+photo+axial, y dV/dt=net/C. Corriente entrante
    positiva; la fotocorriente es una variación negativa, no corriente oscura
    absoluta. Este desglose no identifica especies iónicas de la fuga.
    """
    times = np.asarray(t_ms, dtype=float)
    voltage = np.asarray(voltage_mv, dtype=float)
    if times.ndim > 1 or not np.all(np.isfinite(times)):
        raise ValueError("t_ms debe ser un escalar o vector finito")
    expected_shape = (3,) if times.ndim == 0 else (3, times.size)
    if voltage.shape != expected_shape or not np.all(np.isfinite(voltage)):
        raise ValueError(f"voltage_mv debe tener forma {expected_shape}, orden O,I,T")
    leak_conductance = np.asarray(parameters.leak_ns)
    reversal = np.asarray(parameters.reversal_mv)
    if times.ndim == 1:
        leak_conductance = leak_conductance[:, None]
        reversal = reversal[:, None]
    leak = -leak_conductance * (voltage-reversal)
    current_oi = np.asarray(parameters.g_oi_ns * (voltage[0]-voltage[1]))
    current_it = np.asarray(parameters.g_it_ns * (voltage[1]-voltage[2]))
    axial = np.stack((-current_oi, current_oi-current_it, current_it))
    zero = np.zeros_like(current_oi)
    photo = np.zeros_like(voltage)
    photo[0] = stimulus.current(times)
    return {"leak_current_pa": leak, "photocurrent_pa": photo,
            "axial_current_oi_pa": current_oi, "axial_current_it_pa": current_it,
            "axial_oi_by_node_pa": np.stack((-current_oi, current_oi, zero)),
            "axial_it_by_node_pa": np.stack((zero, -current_it, current_it)),
            "axial_current_pa": axial, "net_current_pa": leak+photo+axial}


def current_balance(t_ms: float, voltage_mv: ArrayLike, parameters: RodParameters,
                    stimulus: PhotonEvents) -> NDArray[np.float64]:
    """Suma del desglose entrante en pA, forma (3,), orden O,I,T.

    Equivale al lado derecho de C*dV/dt, con V en mV y t en ms.
    El acoplamiento redistribuye carga: no es una entrada a otra célula.
    """
    return decompose_currents(t_ms, voltage_mv, parameters, stimulus)["net_current_pa"]


def rhs(t_ms: float, voltage_mv: ArrayLike, parameters: RodParameters,
        stimulus: PhotonEvents) -> NDArray[np.float64]:
    """dV/dt en mV/ms, forma (3,), orden O,I,T: pA/pF=mV/ms.

    t en ms, V en mV; suma corrientes entrantes con current_balance y divide
    por cada C positiva. Comparte el desglose, no introduce canales activos.
    """
    return current_balance(t_ms, voltage_mv, parameters, stimulus) / parameters.capacitance_pf


@dataclass(frozen=True)
class SimulationResult:
    """Salida muestreada: voltage_mv tiene forma (3, número de tiempos)."""

    time_ms: np.ndarray
    voltage_mv: np.ndarray
    photocurrent_pa: np.ndarray
    parameters: RodParameters
    stimulus: PhotonEvents


def simulate(time_ms: ArrayLike, parameters: RodParameters = RodParameters(),
             stimulus: PhotonEvents = PhotonEvents(), *, initial_voltage_mv: ArrayLike | None = None,
             rtol: float = 1e-8, atol: float = 1e-10,
             max_step_ms: float | None = None) -> SimulationResult:
    """Integra sobre el intervalo de `time_ms`, desde el equilibrio por defecto.

    time_ms es un vector creciente (ms); initial_voltage_mv tiene forma (3,).
    Devuelve V en mV (3,n) y fotocorriente pA (n). Parámetros ilustrativos.

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

    def deviation_rhs(t: float, deviation: NDArray[np.float64]) -> NDArray[np.float64]:
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

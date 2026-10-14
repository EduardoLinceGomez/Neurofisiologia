"""Experimentos y medidas del modelo; ninguna función redefine las EDO."""

from collections.abc import Iterable
from dataclasses import replace
from typing import Literal, TypedDict

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import quad_vec
from scipy.linalg import expm

from .model import SimulationResult, conductance_matrix, dark_equilibrium, simulate
from .parameters import RodParameters
from .stimulus import (
    BAYLOR_CELL1_AMPLITUDE_PA, BAYLOR_CELL1_T_PEAK_MS, PhotonEvents, poisson_events,
)


def compare_with_reference(
    time_ms: ArrayLike, *, amplitude_pa: float = BAYLOR_CELL1_AMPLITUDE_PA,
    rate_hz: float = 0.3, seed: int = 2026,
    t_peak_ms: float = BAYLOR_CELL1_T_PEAK_MS,
    modified_parameters: RodParameters = RodParameters(),
) -> tuple[SimulationResult, SimulationResult]:
    """Devuelve (referencia fija, escenario modificado), con V en mV.

    La referencia SIEMPRE usa RodParameters(), A=1.2 pA, t_peak=2200 ms,
    0.3 eventos/s, semilla 2026 y ventana [1000,11000) ms. Ningún control
    modifica estos valores. Ambas salidas usan la misma malla temporal.
    Al variar solo A o parámetros eléctricos se conservan exactamente los
    tiempos de eventos. Al variar tasa/semilla, las realizaciones son distintas:
    una diferencia de voltaje no se atribuye exclusivamente a la tasa.
    La semilla reproduce cada escenario, pero no elimina esa variabilidad.
    No se simula eficiencia cuántica ni flujo óptico por unidad de área.
    """
    reference_stimulus = poisson_events(0.3, 10000, seed=2026, start_ms=1000)
    modified_stimulus = poisson_events(
        rate_hz, 10000, seed=seed, start_ms=1000,
        amplitude_pa=amplitude_pa, t_peak_ms=t_peak_ms,
    )
    reference = simulate(time_ms, RodParameters(), reference_stimulus)
    modified = simulate(time_ms, modified_parameters, modified_stimulus)
    return reference, modified


class ResponseMetrics(TypedDict):
    """Medidas de mínimos muestreados; los retrasos no son tiempos de conducción."""

    min_delta_mv: NDArray[np.float64]
    time_min_ms: NDArray[np.float64]
    delay_i_ms: float | None
    delay_t_ms: float | None
    transmission_ratio: float | None


def voltage_deviation(result: SimulationResult) -> NDArray[np.float64]:
    """ΔV=V-V_dark en mV, forma (3,n), orden O,I,T; E puede ser distinto."""
    return result.voltage_mv-dark_equilibrium(result.parameters)[:, None]


def response_metrics(result: SimulationResult, *, zero_tolerance_mv: float = 1e-8) -> ResponseMetrics:
    """Mínimos de ΔV (mV), instantes/retrasos (ms) y transmisión adimensional.

    El mínimo se localiza en la malla de salida, sin interpolación: un mínimo
    en el extremo final indica que puede faltar recuperación. Si min ΔV no
    es menor que -zero_tolerance_mv no hay hiperpolarización resuelta: su
    instante es NaN y un retraso que la use es None. El cociente
    |min ΔV_T|/|min ΔV_O| es None sin respuesta en O y cero con T nula.
    Se comparan máximos locales de hiperpolarización, no velocidad de propagación.
    """
    if not np.isfinite(zero_tolerance_mv) or zero_tolerance_mv < 0:
        raise ValueError("zero_tolerance_mv debe ser finita y no negativa")
    deviation = voltage_deviation(result)
    minima = deviation.min(axis=1)
    responding = minima < -zero_tolerance_mv
    peak_times = result.time_ms[np.argmin(deviation, axis=1)].astype(float)
    peak_times[~responding] = np.nan
    delay_i = float(peak_times[1]-peak_times[0]) if responding[0] and responding[1] else None
    delay_t = float(peak_times[2]-peak_times[0]) if responding[0] and responding[2] else None
    ratio = None
    if responding[0]:
        ratio = float(abs(minima[2])/abs(minima[0])) if responding[2] else 0.0
    return {"min_delta_mv": minima, "time_min_ms": peak_times,
            "delay_i_ms": delay_i, "delay_t_ms": delay_t, "transmission_ratio": ratio}


def rc_step_response(time_ms: ArrayLike, *, capacitance_pf: float = 20,
                     leak_ns: float = .05, reversal_mv: float = -40,
                     current_pa: float = -1.2, onset_ms: float = 1000) -> NDArray[np.float64]:
    """Solución analítica V=E+(I0/gL)(1-exp(-(t-t0)/τ)), τ=C/gL (ms).

    V inicia en E (mV); una corriente constante I0 (pA) se mantiene desde t0.
    Antes de t0, V=E. C (pF) y gL (nS) son positivos. Devuelve mV con la
    forma de time_ms; usa expm1 para tiempos pequeños. Es un experimento RC
    didáctico, NO una fotocorriente ni un cambio del integrador de producción.
    """
    times = np.asarray(time_ms, dtype=float)
    if not np.all(np.isfinite(times)):
        raise ValueError("time_ms debe ser finito")
    for name, value in (("capacitance_pf", capacitance_pf), ("leak_ns", leak_ns)):
        if not np.isfinite(value) or value <= 0:
            raise ValueError(f"{name} debe ser positivo y finito")
    if not all(np.isfinite(x) for x in (reversal_mv, current_pa, onset_ms)):
        raise ValueError("E, I0 y t0 deben ser finitos")
    elapsed = np.maximum(times-onset_ms, 0)
    tau_ms = capacitance_pf/leak_ns
    return np.asarray(reversal_mv-current_pa/leak_ns*np.expm1(-elapsed/tau_ms))


def modal_times_ms(parameters: RodParameters = RodParameters()) -> NDArray[np.float64]:
    """Constantes de tiempo de modos en ms, orden creciente.

    C^(-1)K es similar a C^(-1/2)K C^(-1/2), simétrica definida positiva.
    Sus autovalores (1/ms) son reales positivos; τ_m=1/λ_m. No son las
    tres C_j/gL_j, salvo desacoplamiento, ni identifican canales activos.
    """
    inverse_sqrt_c = np.diag(1/np.sqrt(parameters.capacitance_pf))
    symmetric_decay = inverse_sqrt_c @ conductance_matrix(parameters) @ inverse_sqrt_c
    return np.sort(1/np.linalg.eigvalsh(symmetric_decay))


def variation_of_constants(time_ms: ArrayLike, parameters: RodParameters,
                            stimulus: PhotonEvents, *,
                            initial_voltage_mv: ArrayLike | None = None) -> NDArray[np.float64]:
    """V (mV), forma (3,n), por exponencial matricial y cuadratura independiente.

    u(t)=exp(MΔt)u0+∫exp(M(t-s))C^(-1)eO I(s)ds, M=-C^(-1)K.
    Esta identidad es exacta para las EDO lineales; expm y quad_vec son
    evaluaciones numéricas, NO una curva exacta ni un dato experimental.
    t (ms) debe ser un vector creciente; iniciar antes del primer evento o
    pasar un estado con historia correcta. No sustituye solve_ivp en producción.
    """
    times = np.asarray(time_ms, dtype=float)
    if times.ndim != 1 or len(times) < 2 or not np.all(np.isfinite(times)) or np.any(np.diff(times) <= 0):
        raise ValueError("time_ms debe ser un vector finito estrictamente creciente")
    rest = dark_equilibrium(parameters)
    initial = rest if initial_voltage_mv is None else np.asarray(initial_voltage_mv, dtype=float)
    if initial.shape != (3,) or not np.all(np.isfinite(initial)):
        raise ValueError("initial_voltage_mv requiere tres valores finitos")
    inverse_c = np.diag(1/np.asarray(parameters.capacitance_pf))
    decay = -inverse_c @ conductance_matrix(parameters)
    input_vector = inverse_c @ np.array([1., 0., 0.])
    columns = []
    start = times[0]
    for time in times:
        forcing = np.zeros(3)
        if time > start:
            event_boundaries = [t for t in stimulus.times_ms if start < t < time]
            forcing = quad_vec(
                lambda s: expm(decay*(time-s)) @ input_vector * stimulus.current(s),
                start, time, epsabs=1e-9, epsrel=1e-9, points=event_boundaries,
            )[0]
        columns.append(rest+expm(decay*(time-start))@(initial-rest)+forcing)
    return np.column_stack(columns)


def sensitivity_map(g_oi_ns: ArrayLike, g_it_ns: ArrayLike, time_ms: ArrayLike,
                     stimulus: PhotonEvents, *, parameters: RodParameters = RodParameters(),
                     metric: Literal["terminal_amplitude_mv", "transmission_ratio"] = "terminal_amplitude_mv") -> NDArray[np.float64]:
    """Barrido 2D: filas g_IT, columnas g_OI (nS), misma entrada y C/gL/E.

    terminal_amplitude_mv=|min ΔV_T| (mV); transmission_ratio=|min ΔV_T|/
    |min ΔV_O| (adimensional), NaN sin respuesta O. Cada celda es un cálculo
    con solve_ivp sobre la malla dada, no calibración ni derivada local.
    """
    values_oi, values_it = np.asarray(g_oi_ns, dtype=float), np.asarray(g_it_ns, dtype=float)
    for values in (values_oi, values_it):
        if values.ndim != 1 or values.size == 0 or not np.all(np.isfinite(values)) or np.any(values < 0) or np.any(np.diff(values) <= 0):
            raise ValueError("Las conductancias requieren vectores no negativos, crecientes y finitos")
    if metric not in ("terminal_amplitude_mv", "transmission_ratio"):
        raise ValueError("Métrica de sensibilidad desconocida")
    grid = np.empty((len(values_it), len(values_oi)))
    for row, conductance_it in enumerate(values_it):
        for column, conductance_oi in enumerate(values_oi):
            varied = replace(parameters, g_oi_ns=conductance_oi, g_it_ns=conductance_it)
            measures = response_metrics(simulate(time_ms, varied, stimulus))
            value = abs(measures["min_delta_mv"][2]) if metric == "terminal_amplitude_mv" else measures["transmission_ratio"]
            grid[row, column] = np.nan if value is None else value
    return grid


def poisson_ensemble(time_ms: ArrayLike, rate_hz: float, seeds: Iterable[int], *,
                      parameters: RodParameters = RodParameters(),
                      amplitude_pa: float = 1.2, t_peak_ms: float = 2200) -> tuple[SimulationResult, ...]:
    """Realizaciones Poisson independientes reproducibles en [1000,11000) ms.

    rate_hz tiene unidades eventos efectivos/s. Cada semilla genera una entrada
    y su V (mV); no modifica el RNG global. La media sobre una muestra finita
    no es una medición ni un efecto de tasa libre de azar. Se exige ≥1 semilla.
    """
    seed_values = tuple(seeds)
    if not seed_values:
        raise ValueError("Se requiere al menos una semilla")
    if len(set(seed_values)) != len(seed_values):
        raise ValueError("Usa semillas distintas para realizaciones independientes")
    return tuple(simulate(time_ms, parameters, poisson_events(
        rate_hz, 10000, seed=seed, start_ms=1000, amplitude_pa=amplitude_pa,
        t_peak_ms=t_peak_ms)) for seed in seed_values)

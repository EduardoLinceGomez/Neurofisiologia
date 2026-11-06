"""M0: tres células de un compartimento y dos sinapsis químicas efectivas.

Unidades ms, mV, pF, nS, pA. L y r son adimensionales, no calibrados.
La inversión ON reside exclusivamente en g_ON(r), nunca en el voltaje.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.integrate import solve_ivp
from scipy.special import expit


@dataclass(frozen=True)
class M0Parameters:
    """Constantes ilustrativas, sin especie asignada; orden cono, ON, OFF.

    Las C y fugas son totales por célula. E_syn > E_L asegura una corriente
    catiónica despolarizante en reposo; cero g_max desconecta solo esa sinapsis.
    light_gain_pa mide pA por unidad de iluminación normalizada.
    """

    capacitance_pf: tuple[float, float, float] = (20.0, 30.0, 30.0)
    leak_ns: tuple[float, float, float] = (1.0, 1.0, 1.0)
    leak_reversal_mv: tuple[float, float, float] = (-40.0, -60.0, -60.0)
    synaptic_reversal_mv: tuple[float, float] = (0.0, 0.0)
    g_on_max_ns: float = 0.5
    g_off_max_ns: float = 0.5
    light_gain_pa: float = 10.0
    release_half_mv: float = -40.0
    release_slope_mv: float = 5.0

    def __post_init__(self) -> None:
        for name, size in (("capacitance_pf", 3), ("leak_ns", 3),
                           ("leak_reversal_mv", 3), ("synaptic_reversal_mv", 2)):
            values = np.asarray(getattr(self, name), dtype=float)
            if values.shape != (size,) or not np.all(np.isfinite(values)):
                raise ValueError(f"{name} requiere {size} valores finitos")
            if name in ("capacitance_pf", "leak_ns") and np.any(values <= 0):
                raise ValueError(f"{name} debe ser positivo")
            object.__setattr__(self, name, tuple(float(v) for v in values))
        for name in ("light_gain_pa", "release_slope_mv", "g_on_max_ns", "g_off_max_ns", "release_half_mv"):
            value = getattr(self, name)
            if not np.isscalar(value) or not np.isfinite(value):
                raise ValueError(f"{name} debe ser un escalar finito")
        if self.light_gain_pa <= 0 or self.release_slope_mv <= 0:
            raise ValueError("La ganancia de luz y la pendiente de liberación deben ser positivas")
        if min(self.g_on_max_ns, self.g_off_max_ns) < 0:
            raise ValueError("Las conductancias máximas no pueden ser negativas")
        if np.any(np.asarray(self.synaptic_reversal_mv) <= np.asarray(self.leak_reversal_mv[1:])):
            raise ValueError("M0 requiere E_syn mayor que E_L en cada bipolar")


@dataclass(frozen=True)
class LightStep:
    """Nivel absoluto de L >= 0 durante [start_ms, end_ms); no es fotocorriente."""

    start_ms: float
    end_ms: float
    level: float

    def __post_init__(self) -> None:
        if not np.all(np.isfinite((self.start_ms, self.end_ms, self.level))):
            raise ValueError("Los tiempos y L deben ser finitos")
        if self.end_ms <= self.start_ms or self.level < 0:
            raise ValueError("El intervalo debe tener duración positiva y L >= 0")


@dataclass(frozen=True)
class LightProtocol:
    """Fondo L0 > 0 y pasos no solapados; al terminar cada paso vuelve a L0.

    Los pasos pueden ser contiguos. Se ordenan en una tupla inmutable;
    evaluar instantes en cualquier orden no altera el protocolo.
    """

    background: float = 1.0
    steps: tuple[LightStep, ...] = ()

    def __post_init__(self) -> None:
        if not np.isfinite(self.background) or self.background <= 0:
            raise ValueError("El fondo L0 debe ser finito y positivo")
        steps = tuple(self.steps)
        if not all(isinstance(step, LightStep) for step in steps):
            raise ValueError("steps debe contener objetos LightStep")
        ordered = tuple(sorted(steps, key=lambda step: step.start_ms))
        if any(a.end_ms > b.start_ms for a, b in zip(ordered, ordered[1:])):
            raise ValueError("Los pasos de iluminación no pueden solaparse")
        object.__setattr__(self, "steps", ordered)

    def illumination(self, time_ms: ArrayLike) -> NDArray[np.float64]:
        """L(t) adimensional, continua por la derecha; admite tiempos desordenados."""
        times = np.asarray(time_ms, dtype=float)
        if not np.all(np.isfinite(times)):
            raise ValueError("Los tiempos deben ser finitos")
        light = np.full_like(times, self.background, dtype=float)
        for step in self.steps:
            light = np.where((times >= step.start_ms) & (times < step.end_ms), step.level, light)
        return light


def release_fraction(cone_voltage_mv: ArrayLike, parameters: M0Parameters = M0Parameters()) -> NDArray[np.float64]:
    """r(V_C) creciente; sigmoide estable, sin EDO de vesículas ni concentración.

    Matemáticamente 0<r<1; en coma flotante puede redondearse a 0 o 1.
    """
    voltage = np.asarray(cone_voltage_mv, dtype=float)
    if not np.all(np.isfinite(voltage)):
        raise ValueError("V_C debe ser finito")
    with np.errstate(over="ignore"):
        return np.asarray(expit((voltage - parameters.release_half_mv) / parameters.release_slope_mv))


def synaptic_conductances(release: ArrayLike, parameters: M0Parameters = M0Parameters()) -> NDArray[np.float64]:
    """g_ON=gmax_ON(1-r), g_OFF=gmax_OFF*r, en nS; forma (2, ...).

    mGluR6 controla indirectamente la apertura catiónica ON. No es una
    conductancia negativa ni una sinapsis de Cl-. OFF representa iGluR.
    """
    fraction = np.asarray(release, dtype=float)
    if not np.all(np.isfinite(fraction)) or np.any((fraction < 0) | (fraction > 1)):
        raise ValueError("r debe estar entre 0 y 1")
    return np.stack((parameters.g_on_max_ns * (1-fraction), parameters.g_off_max_ns * fraction))


def photocurrent_pa(illumination: ArrayLike, background: float,
                    parameters: M0Parameters = M0Parameters()) -> NDArray[np.float64]:
    """Variación entrante -k_L(L-L0), pA; no representa corriente oscura absoluta."""
    light = np.asarray(illumination, dtype=float)
    if not np.isfinite(background) or background <= 0 or not np.all(np.isfinite(light)) or np.any(light < 0):
        raise ValueError("Se requiere L >= 0 finita y L0 > 0 finito")
    return -parameters.light_gain_pa * (light-background)


def background_equilibrium(parameters: M0Parameters = M0Parameters()) -> NDArray[np.float64]:
    """Equilibrio cerrado en L=L0, en mV; las bipolares no parten de E_L."""
    cone = parameters.leak_reversal_mv[0]
    conductance = synaptic_conductances(release_fraction(cone, parameters), parameters)
    leak = np.asarray(parameters.leak_ns[1:])
    bipolar = (leak*np.asarray(parameters.leak_reversal_mv[1:])
               + conductance*np.asarray(parameters.synaptic_reversal_mv)) / (leak+conductance)
    return np.r_[cone, bipolar]


def constant_light_equilibrium(level: float, background: float = 1.0,
                               parameters: M0Parameters = M0Parameters()) -> NDArray[np.float64]:
    """Equilibrio de un nivel constante; útil para separar amplitud final y transitorio."""
    cone = parameters.leak_reversal_mv[0] + float(photocurrent_pa(level, background, parameters))/parameters.leak_ns[0]
    conductance = synaptic_conductances(release_fraction(cone, parameters), parameters)
    leak = np.asarray(parameters.leak_ns[1:])
    bipolar = (leak*np.asarray(parameters.leak_reversal_mv[1:])
               + conductance*np.asarray(parameters.synaptic_reversal_mv)) / (leak+conductance)
    return np.r_[cone, bipolar]


def current_components(voltage_mv: ArrayLike, illumination: ArrayLike, background: float,
                       parameters: M0Parameters = M0Parameters()) -> dict[str, NDArray[np.float64]]:
    """Corrientes entrantes en pA, orden C/ON/OFF, forma (3,) o (3,n).

    La señal química modifica g; no hay corriente axial entre estas células.
    El cono no recibe una corriente igual y opuesta a la de las bipolares.
    """
    voltage = np.asarray(voltage_mv, dtype=float)
    light = np.asarray(illumination, dtype=float)
    if light.ndim > 1 or voltage.shape != (3,)+light.shape or not np.all(np.isfinite(voltage)):
        raise ValueError("V debe tener forma (3,) para L escalar o (3,n) para L vector")
    shape = (3,) + (1,)*light.ndim
    leak = -np.asarray(parameters.leak_ns).reshape(shape)*(voltage-np.asarray(parameters.leak_reversal_mv).reshape(shape))
    photo = np.zeros_like(voltage)
    photo[0] = photocurrent_pa(light, background, parameters)
    synaptic = np.zeros_like(voltage)
    conductance = synaptic_conductances(release_fraction(voltage[0], parameters), parameters)
    reversal = np.asarray(parameters.synaptic_reversal_mv).reshape((2,)+(1,)*light.ndim)
    synaptic[1:] = conductance*(reversal-voltage[1:])
    return {"leak_pa": leak, "photo_pa": photo, "synaptic_pa": synaptic,
            "net_pa": leak+photo+synaptic}


def rhs(time_ms: float, voltage_mv: ArrayLike, parameters: M0Parameters,
        protocol: LightProtocol) -> NDArray[np.float64]:
    """Tres EDO dV/dt = suma de corrientes entrantes/C, en mV/ms."""
    currents = current_components(voltage_mv, protocol.illumination(time_ms), protocol.background, parameters)
    return currents["net_pa"] / parameters.capacitance_pf


@dataclass(frozen=True)
class M0Result:
    """Trayectorias simuladas (no medidas); V y delta_V tienen orden C/ON/OFF."""

    time_ms: NDArray[np.float64]
    voltage_mv: NDArray[np.float64]
    illumination: NDArray[np.float64]
    photo_pa: NDArray[np.float64]
    release: NDArray[np.float64]
    conductance_ns: NDArray[np.float64]
    equilibrium_mv: NDArray[np.float64]
    parameters: M0Parameters
    protocol: LightProtocol

    @property
    def delta_voltage_mv(self) -> NDArray[np.float64]:
        """Desviación respecto al equilibrio del propio conjunto de parámetros."""
        return self.voltage_mv-self.equilibrium_mv[:, None]


def simulate_m0(time_ms: ArrayLike, parameters: M0Parameters = M0Parameters(),
                protocol: LightProtocol = LightProtocol(), *,
                initial_voltage_mv: ArrayLike | None = None,
                rtol: float = 1e-8, atol: float = 1e-10,
                max_step_ms: float = np.inf) -> M0Result:
    """Integra con solve_ivp, separando exactamente cada discontinuidad de L.

    La malla de salida no controla qué pulsos ve el integrador: incluso un pulso
    entre dos muestras se integra. Por defecto se exige que el primer paso no
    preceda al inicio; una continuación requiere proporcionar el estado inicial.
    Se integra V-V* para controlar errores sobre respuestas pequeñas. No se
    impone signo ni se recortan los voltajes después de integrar.
    """
    times = np.asarray(time_ms, dtype=float)
    if times.ndim != 1 or times.size < 2 or not np.all(np.isfinite(times)) or np.any(np.diff(times) <= 0):
        raise ValueError("time_ms debe ser un vector finito estrictamente creciente")
    if any(not np.isfinite(v) or v <= 0 for v in (rtol, atol)) or np.isnan(max_step_ms) or max_step_ms <= 0:
        raise ValueError("Tolerancias y max_step_ms deben ser positivos")
    if initial_voltage_mv is None and any(step.start_ms < times[0] for step in protocol.steps):
        raise ValueError("El estímulo precede al inicio; proporcionar el estado inicial o iniciar antes")
    equilibrium = background_equilibrium(parameters)
    initial = equilibrium if initial_voltage_mv is None else np.asarray(initial_voltage_mv, dtype=float)
    if initial.shape != (3,) or not np.all(np.isfinite(initial)):
        raise ValueError("El estado inicial debe contener tres voltajes finitos")
    edges = sorted({float(times[0]), float(times[-1]),
                    *(t for step in protocol.steps for t in (step.start_ms, step.end_ms)
                      if times[0] < t < times[-1])})
    deviation = initial-equilibrium
    voltage = np.empty((3, times.size))
    for left, right in zip(edges, edges[1:]):
        # El valor interior es constante: ningún paso cruza un salto de entrada.
        level = protocol.illumination(left+(right-left)/2)

        def derivative(t: float, state: NDArray[np.float64]) -> NDArray[np.float64]:
            return current_components(state+equilibrium, level, protocol.background, parameters)["net_pa"] / parameters.capacitance_pf

        solution = solve_ivp(derivative, (left, right), deviation, dense_output=True,
                             rtol=rtol, atol=atol, max_step=max_step_ms)
        if not solution.success:
            raise RuntimeError(f"Integración M0 incompleta: {solution.message}")
        mask = (times >= left) & (times <= right)
        if np.any(mask):
            voltage[:, mask] = equilibrium[:, None]+solution.sol(times[mask])
        deviation = solution.y[:, -1]
    if not np.all(np.isfinite(voltage)):
        raise RuntimeError("La simulación produjo voltajes no finitos")
    light = protocol.illumination(times)
    release = release_fraction(voltage[0], parameters)
    return M0Result(times.copy(), voltage, light, photocurrent_pa(light, protocol.background, parameters),
                    release, synaptic_conductances(release, parameters), equilibrium, parameters, protocol)

"""Fotocorriente impuesta: variación negativa de corriente entrante.

Los eventos representan respuestas elementales ya generadas, no el flujo de
fotones incidentes ni spikes neuronales. No se modela eficiencia cuántica.
"""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Iterable

import numpy as np
from numpy.typing import ArrayLike, NDArray

# Referencia de sapo, célula 1 (Baylor, Lamb y Yau 1979); no ajuste de voltaje.
BAYLOR_CELL1_AMPLITUDE_PA = 1.2
BAYLOR_CELL1_T_PEAK_MS = 2200.0


def photon_kernel(u_ms: ArrayLike, t_peak_ms: float = BAYLOR_CELL1_T_PEAK_MS) -> float | NDArray[np.float64]:
    """h(u) causal y de máximo 1; aproximación fenomenológica de cuatro etapas.

    h(u) = (u/t_peak)^3 exp(3(1-u/t_peak)), u >= 0.
    u y t_peak están en ms. Devuelve h adimensional, escalar o array de la
    misma forma que u. No representa cuatro reacciones moleculares.
    Se evalúa en dominio logarítmico para evitar overflow en tiempos grandes.
    """
    if not np.isfinite(t_peak_ms) or t_peak_ms <= 0:
        raise ValueError("t_peak_ms debe ser finito y positivo")
    u = np.asarray(u_ms, dtype=float)
    if not np.all(np.isfinite(u)):
        raise ValueError("u_ms debe contener tiempos finitos")
    h = np.zeros_like(u)
    positive = u > 0
    with np.errstate(over="ignore", under="ignore"):
        x = u[positive] / t_peak_ms
        finite = np.isfinite(x) & (x > 0)
        values = np.zeros_like(x)
        values[finite] = np.exp(3 * (np.log(x[finite]) + 1 - x[finite]))
        h[positive] = values
    return float(h) if h.ndim == 0 else h


@dataclass(frozen=True)
class PhotonEvents:
    """Eventos en ms y amplitudes positivas en pA; se permite coincidencia.

    Cada instante debe tener su amplitud. `from_times` asigna una misma amplitud
    a todos los eventos. El tren vacío representa oscuridad (variación cero).
    """

    times_ms: tuple[float, ...] = ()
    amplitudes_pa: tuple[float, ...] = ()
    t_peak_ms: float = BAYLOR_CELL1_T_PEAK_MS

    def __post_init__(self) -> None:
        times = np.asarray(self.times_ms, dtype=float)
        amps = np.asarray(self.amplitudes_pa, dtype=float)
        if times.ndim != 1 or amps.shape != times.shape:
            raise ValueError("Se requiere una amplitud por evento en un vector")
        if not np.all(np.isfinite(times)) or np.any(times < 0):
            raise ValueError("Los eventos deben tener tiempos finitos no negativos")
        if np.any(np.diff(times) < 0):
            raise ValueError("Los eventos deben estar ordenados por tiempo")
        if not np.all(np.isfinite(amps)) or np.any(amps < 0):
            raise ValueError("Las amplitudes deben ser finitas y no negativas")
        photon_kernel(0.0, self.t_peak_ms)  # valida el tiempo al máximo
        object.__setattr__(self, "times_ms", tuple(float(x) for x in times))
        object.__setattr__(self, "amplitudes_pa", tuple(float(x) for x in amps))
        object.__setattr__(self, "t_peak_ms", float(self.t_peak_ms))

    @classmethod
    def from_times(cls: type[PhotonEvents], times_ms: Iterable[float],
                   amplitude_pa: float = BAYLOR_CELL1_AMPLITUDE_PA,
                   t_peak_ms: float = BAYLOR_CELL1_T_PEAK_MS) -> PhotonEvents:
        """Asigna A≥0 (pA) a tiempos ordenados en ms, sin modificar su orden.

        h tiene máximo unitario en t_peak_ms; por tanto cada variación entrante
        vale -A*h. Coincidencias se suman, sin saturación ni adaptación.
        """
        times = tuple(times_ms)
        if not np.isfinite(amplitude_pa) or amplitude_pa < 0:
            raise ValueError("amplitude_pa debe ser finita y no negativa")
        return cls(times, (amplitude_pa,) * len(times), t_peak_ms)

    def current(self, t_ms: ArrayLike) -> float | NDArray[np.float64]:
        """I_photo(t) en pA: -sum_k A_k h(t-t_k), sin saturación.

        t_ms finito, escalar o array; devuelve la misma forma. A≥0 produce
        variación entrante no positiva; no es la corriente oscura absoluta.
        """
        t = np.asarray(t_ms, dtype=float)
        if not np.all(np.isfinite(t)):
            raise ValueError("t_ms debe ser finito")
        total = np.zeros_like(t)
        for event, amplitude in zip(self.times_ms, self.amplitudes_pa):
            total -= amplitude * photon_kernel(t - event, self.t_peak_ms)
        return float(total) if total.ndim == 0 else total


def poisson_events(rate_hz: float, duration_ms: float, *, seed: int,
                   start_ms: float = 0.0,
                   amplitude_pa: float = BAYLOR_CELL1_AMPLITUDE_PA,
                   t_peak_ms: float = BAYLOR_CELL1_T_PEAK_MS) -> PhotonEvents:
    """Proceso Poisson homogéneo en [start, start+duration), con RNG local.

    Se sortea N ~ Poisson(rate_hz * duration_ms / 1000) y, condicionado a N,
    tiempos uniformes ordenados. No modifica el generador global de NumPy.
    La tasa es de eventos efectivos, no una intensidad óptica calibrada.
    """
    for name, value in (("rate_hz", rate_hz), ("duration_ms", duration_ms),
                        ("start_ms", start_ms)):
        if not np.isfinite(value) or value < 0:
            raise ValueError(f"{name} debe ser finito y no negativo")
    if not np.isfinite(start_ms + duration_ms):
        raise ValueError("El final de la ventana debe ser finito")
    if isinstance(seed, bool) or not isinstance(seed, (int, np.integer)) or seed < 0:
        raise ValueError("seed debe ser un entero no negativo explícito")
    rng = np.random.default_rng(seed)
    count = rng.poisson(rate_hz * duration_ms / 1000.0)
    times = np.sort(rng.uniform(start_ms, start_ms + duration_ms, count))
    return PhotonEvents.from_times(times, amplitude_pa, t_peak_ms)

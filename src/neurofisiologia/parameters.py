"""Parámetros eléctricos ilustrativos y no calibrados, ordenados O, I, T."""

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class RodParameters:
    """Valores totales por compartimento, no densidades por área.

    Cada fuga es positiva para que el equilibrio oscuro sea único incluso si
    se desacoplan los compartimentos. Los E no tienen que ser iguales.
    """

    capacitance_pf: tuple[float, float, float] = (20.0, 15.0, 5.0)
    leak_ns: tuple[float, float, float] = (0.05, 0.10, 0.05)
    reversal_mv: tuple[float, float, float] = (-40.0, -40.0, -40.0)
    g_oi_ns: float = 0.10
    g_it_ns: float = 0.10

    def __post_init__(self) -> None:
        for name in ("capacitance_pf", "leak_ns", "reversal_mv"):
            values = np.asarray(getattr(self, name), dtype=float)
            if values.shape != (3,) or not np.all(np.isfinite(values)):
                raise ValueError(f"{name}: se requieren tres valores finitos (O, I, T)")
            if name != "reversal_mv" and np.any(values <= 0):
                raise ValueError(f"{name}: todos los valores deben ser positivos")
            object.__setattr__(self, name, tuple(float(x) for x in values))
        for name in ("g_oi_ns", "g_it_ns"):
            value = float(getattr(self, name))
            if not np.isfinite(value) or value < 0:
                raise ValueError(f"{name}: debe ser finito y no negativo")
            object.__setattr__(self, name, value)

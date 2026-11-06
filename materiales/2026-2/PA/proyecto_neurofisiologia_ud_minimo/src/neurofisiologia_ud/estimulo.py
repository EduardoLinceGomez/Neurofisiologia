"""Definiciones de estímulos transmembranales."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class PulsoRectangular:
    """Representa un pulso rectangular simple.

    Parameters
    ----------
    inicio_ms:
        Tiempo de inicio del pulso, en milisegundos.
    duracion_ms:
        Duración del pulso, en milisegundos.
    amplitud:
        Amplitud del forzamiento `J_F`.
    """

    inicio_ms: float
    duracion_ms: float
    amplitud: float

    def evaluar(self, t: np.ndarray) -> np.ndarray:
        """Evalúa el pulso sobre un vector temporal."""
        mascara = (t >= self.inicio_ms) & (t < self.inicio_ms + self.duracion_ms)
        salida = np.zeros_like(t, dtype=float)
        salida[mascara] = self.amplitud
        return salida


class ProtocoloPulsos:
    """Agrupa uno o varios pulsos rectangulares."""

    def __init__(self, pulsos: list[PulsoRectangular] | None = None) -> None:
        self.pulsos = pulsos or []

    def agregar(self, pulso: PulsoRectangular) -> None:
        """Agrega un pulso al protocolo."""
        self.pulsos.append(pulso)

    def vector_estimulo(self, t: np.ndarray) -> np.ndarray:
        """Suma la contribución de todos los pulsos sobre `t`."""
        salida = np.zeros_like(t, dtype=float)
        for pulso in self.pulsos:
            salida += pulso.evaluar(t)
        return salida

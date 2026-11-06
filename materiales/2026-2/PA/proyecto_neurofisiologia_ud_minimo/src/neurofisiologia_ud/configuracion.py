"""Objetos de configuración para rejillas y tiempos del proyecto."""

from __future__ import annotations

from dataclasses import dataclass, field
import numpy as np


@dataclass(frozen=True)
class RejillaUmbral:
    """Define la rejilla usada para construir un caché de umbral.

    Attributes
    ----------
    amplitudes:
        Valores posibles de la amplitud del pulso `J_F`.
    duraciones:
        Valores posibles de la duración del pulso, en milisegundos.
    dt:
        Paso temporal del integrador, en milisegundos.
    t_max:
        Tiempo máximo de simulación, en milisegundos.
    tipo:
        Tipo numérico usado para tensores y almacenamiento.
    """

    amplitudes: np.ndarray = field(default_factory=lambda: np.array([0.0, 20.0, 30.0, 40.0, 50.0], dtype=np.float32))
    duraciones: np.ndarray = field(default_factory=lambda: np.array([0.5, 1.0, 2.0, 4.0], dtype=np.float32))
    dt: float = 0.02
    t_max: float = 40.0
    tipo: np.dtype = np.float32

    def __post_init__(self) -> None:
        object.__setattr__(self, "amplitudes", np.asarray(self.amplitudes, dtype=self.tipo))
        object.__setattr__(self, "duraciones", np.asarray(self.duraciones, dtype=self.tipo))

    @property
    def tiempos(self) -> np.ndarray:
        """Devuelve el vector temporal global asociado a la rejilla."""
        return np.arange(0.0, self.t_max + self.dt, self.dt, dtype=self.tipo)


def rejilla_umbral_ejemplo() -> RejillaUmbral:
    """Construye una rejilla pequeña y útil para pruebas y demostraciones."""
    return RejillaUmbral(
        amplitudes=np.array([0.0, 20.0, 30.0, 40.0, 50.0, 60.0], dtype=np.float32),
        duraciones=np.array([0.5, 1.0, 2.0, 4.0], dtype=np.float32),
        dt=0.02,
        t_max=40.0,
        tipo=np.float32,
    )

"""Funciones de análisis geométrico y de trayectorias para el sistema UD-básico."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from .modelos.sistema_ud import SistemaUDBasico


@dataclass
class ResumenPulso:
    """Resumen simple de una trayectoria de `v(t)`."""

    hay_pulso: bool
    v_max: float
    t_v_max: float
    v_min: float
    t_v_min: float


class AnalizadorUDBasico:
    """Agrupa cálculos de análisis para reuso desde scripts y notebooks."""

    def __init__(self, modelo: SistemaUDBasico) -> None:
        self.modelo = modelo

    def resumen_pulso(self, t: np.ndarray, v: np.ndarray, umbral_v: float = 0.0) -> ResumenPulso:
        """Construye un resumen elemental de una trayectoria de voltaje."""
        indice_max = int(np.argmax(v))
        indice_min = int(np.argmin(v))
        return ResumenPulso(
            hay_pulso=bool(v[indice_max] > umbral_v),
            v_max=float(v[indice_max]),
            t_v_max=float(t[indice_max]),
            v_min=float(v[indice_min]),
            t_v_min=float(t[indice_min]),
        )

    def curva_umbral(self, v: np.ndarray, j_f: float) -> np.ndarray:
        """Evalúa la curva de umbral `T(v)` del plano fase.

        Sigue la estructura algebraica de las ecuaciones `(2.44)-(2.45)`
        en la sección de cálculos del modelo minimal.
        """
        p = self.modelo.parametros
        s_m = self.modelo.S_m(v)
        h = self.modelo.H(v, j_f)
        d = self.modelo.D(v)
        rho = self.modelo.rho(v)
        alpha = self.modelo.alpha(v)
        k = p.a_up * s_m * (1.0 + p.s_m * (v - p.v_up) * (1.0 - s_m))
        a_coef = p.a_dn * d
        b_coef = k * d - p.a_dn * h + d * rho
        c_coef = -k * h - d * alpha
        discriminante = b_coef * b_coef - 4.0 * a_coef * c_coef
        salida = np.full_like(v, fill_value=np.nan, dtype=float)
        mascara = (np.abs(a_coef) > 1e-12) & (discriminante >= 0.0)
        salida[mascara] = (
            -b_coef[mascara] - np.sqrt(discriminante[mascara])
        ) / (2.0 * a_coef[mascara])
        return salida

    def invariantes_lineales(self, v_fijo: float, w_fijo: float, j_f: float) -> dict[str, float]:
        """Devuelve traza, determinante y discriminante de la jacobiana."""
        j = self.modelo.jacobiana_vw(v_fijo, w_fijo, j_f)
        traza = float(np.trace(j))
        determinante = float(np.linalg.det(j))
        discriminante = traza * traza - 4.0 * determinante
        return {
            "traza": traza,
            "determinante": determinante,
            "discriminante": discriminante,
        }

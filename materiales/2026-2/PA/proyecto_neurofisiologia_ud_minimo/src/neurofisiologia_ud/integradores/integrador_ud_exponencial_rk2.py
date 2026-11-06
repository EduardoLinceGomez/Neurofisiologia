"""Esquema numérico mixto: actualización exponencial para `w` y RK2 para `v`."""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from ..estimulo import ProtocoloPulsos
from ..modelos.sistema_ud import SistemaUDBasico


@dataclass
class ResultadoSimulacion:
    """Contenedor para una trayectoria individual del sistema UD-básico."""

    t: np.ndarray
    v: np.ndarray
    w: np.ndarray
    j_f: np.ndarray


@dataclass
class ResultadoLoteUmbral:
    """Contenedor para un lote vectorizado de trayectorias de umbral.

    Las matrices `v` y `w` tienen forma `(n_amplitudes, n_duraciones, n_t)`.
    """

    t: np.ndarray
    amplitudes: np.ndarray
    duraciones: np.ndarray
    v: np.ndarray
    w: np.ndarray


class IntegradorUDBasicoExponencialRK2:
    """Integra el sistema UD-básico con un esquema mixto reusable.

    Método
    ------
    - `w` se actualiza mediante la solución exacta del paso con `v` congelado.
    - `v` se integra con RK2 explícito de Heun.

    Este esquema es una buena primera aproximación porque aprovecha la forma
    lineal de la ecuación para `w` sin introducir la complejidad de un método
    totalmente implícito.
    """

    def __init__(self, modelo: SistemaUDBasico, dt: float = 0.02, t_max: float = 40.0, tipo=np.float32) -> None:
        self.modelo = modelo
        self.dt = float(dt)
        self.t_max = float(t_max)
        self.tipo = tipo

    def tiempos(self) -> np.ndarray:
        """Devuelve el vector temporal del integrador."""
        return np.arange(0.0, self.t_max + self.dt, self.dt, dtype=self.tipo)

    def integrar(
        self,
        protocolo: ProtocoloPulsos | None = None,
        j_f_constante: float = 0.0,
        v_inicial: float | None = None,
        w_inicial: float | None = None,
    ) -> ResultadoSimulacion:
        """Integra una trayectoria individual del sistema.

        Parameters
        ----------
        protocolo:
            Protocolo de pulsos a aplicar. Si es `None`, se usa `j_f_constante`.
        j_f_constante:
            Corriente forzada constante si no se usa un protocolo.
        v_inicial, w_inicial:
            Condiciones iniciales. Si son `None`, se toma el punto fijo de reposo.
        """
        t = self.tiempos()
        if protocolo is None:
            j_f = np.full_like(t, fill_value=j_f_constante, dtype=self.tipo)
        else:
            j_f = protocolo.vector_estimulo(t).astype(self.tipo)

        if v_inicial is None or w_inicial is None:
            v0, w0 = self.modelo.punto_fijo_reposo(j_f=0.0)
            v_inicial = float(v0) if v_inicial is None else float(v_inicial)
            w_inicial = float(w0) if w_inicial is None else float(w_inicial)

        v = np.empty_like(t, dtype=self.tipo)
        w = np.empty_like(t, dtype=self.tipo)
        v[0] = v_inicial
        w[0] = w_inicial

        for k in range(t.size - 1):
            dv_0 = self.modelo.dv_dt(v[k], w[k], j_f[k])
            v_predictor = v[k] + self.dt * dv_0
            w_predictor = self.modelo.actualizar_w_exponencial(w[k], v[k], self.dt)
            dv_1 = self.modelo.dv_dt(v_predictor, w_predictor, j_f[k + 1])
            v[k + 1] = v[k] + 0.5 * self.dt * (dv_0 + dv_1)
            w[k + 1] = self.modelo.actualizar_w_exponencial(w[k], v[k + 1], self.dt)

        return ResultadoSimulacion(t=t, v=v, w=w, j_f=j_f)

    def integrar_lote_umbral(
        self,
        amplitudes: np.ndarray,
        duraciones: np.ndarray,
        inicio_ms: float = 0.0,
        v_inicial: float | None = None,
        w_inicial: float | None = None,
    ) -> ResultadoLoteUmbral:
        """Integra un lote completo de trayectorias para construir un caché.

        La vectorización se realiza sobre todas las combinaciones de amplitud y duración.
        Cada trayectoria usa un pulso rectangular con el mismo `inicio_ms`.
        """
        amplitudes = np.asarray(amplitudes, dtype=self.tipo)
        duraciones = np.asarray(duraciones, dtype=self.tipo)
        t = self.tiempos()
        n_t = t.size

        if v_inicial is None or w_inicial is None:
            v0, w0 = self.modelo.punto_fijo_reposo(j_f=0.0)
            v_inicial = float(v0) if v_inicial is None else float(v_inicial)
            w_inicial = float(w0) if w_inicial is None else float(w_inicial)

        amplitud_malla, duracion_malla = np.meshgrid(amplitudes, duraciones, indexing="ij")
        amplitud_plana = amplitud_malla.reshape(-1).astype(self.tipo)
        duracion_plana = duracion_malla.reshape(-1).astype(self.tipo)
        n_trayectorias = amplitud_plana.size

        v_plano = np.empty((n_trayectorias, n_t), dtype=self.tipo)
        w_plano = np.empty((n_trayectorias, n_t), dtype=self.tipo)
        v_plano[:, 0] = v_inicial
        w_plano[:, 0] = w_inicial

        for k in range(n_t - 1):
            mascara_0 = (t[k] >= inicio_ms) & (t[k] < inicio_ms + duracion_plana)
            mascara_1 = (t[k + 1] >= inicio_ms) & (t[k + 1] < inicio_ms + duracion_plana)
            j_f_0 = np.where(mascara_0, amplitud_plana, 0.0)
            j_f_1 = np.where(mascara_1, amplitud_plana, 0.0)

            dv_0 = self.modelo.dv_dt(v_plano[:, k], w_plano[:, k], j_f_0)
            v_predictor = v_plano[:, k] + self.dt * dv_0
            w_predictor = self.modelo.actualizar_w_exponencial(w_plano[:, k], v_plano[:, k], self.dt)
            dv_1 = self.modelo.dv_dt(v_predictor, w_predictor, j_f_1)
            v_plano[:, k + 1] = v_plano[:, k] + 0.5 * self.dt * (dv_0 + dv_1)
            w_plano[:, k + 1] = self.modelo.actualizar_w_exponencial(w_plano[:, k], v_plano[:, k + 1], self.dt)

        forma = (amplitudes.size, duraciones.size, n_t)
        return ResultadoLoteUmbral(
            t=t,
            amplitudes=amplitudes,
            duraciones=duraciones,
            v=v_plano.reshape(forma),
            w=w_plano.reshape(forma),
        )

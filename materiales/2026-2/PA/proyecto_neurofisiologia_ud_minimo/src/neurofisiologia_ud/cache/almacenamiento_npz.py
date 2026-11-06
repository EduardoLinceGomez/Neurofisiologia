"""Clases para guardar y cargar cachés NPZ del sistema UD-básico."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import numpy as np

from ..integradores.integrador_ud_exponencial_rk2 import ResultadoLoteUmbral


def _indice_exacto(valores: np.ndarray, objetivo: float, atol: float = 1e-7) -> int:
    coincidencias = np.where(np.isclose(valores, objetivo, atol=atol))[0]
    if coincidencias.size == 0:
        raise KeyError(f"El valor {objetivo} no pertenece a la rejilla disponible.")
    return int(coincidencias[0])


def _desplazar_serie(y: np.ndarray, pasos: int, valor_inicial: float) -> np.ndarray:
    if pasos <= 0:
        return y.copy()
    salida = np.empty_like(y)
    if pasos >= y.size:
        salida.fill(valor_inicial)
        return salida
    salida[:pasos] = valor_inicial
    salida[pasos:] = y[:-pasos]
    return salida


@dataclass
class CacheUmbralNPZ:
    """Representa un caché de umbral ya cargado en memoria."""

    t: np.ndarray
    amplitudes: np.ndarray
    duraciones: np.ndarray
    v: np.ndarray
    w: np.ndarray
    metadatos: dict

    @property
    def dt(self) -> float:
        """Paso temporal inferido del vector `t`."""
        if self.t.size < 2:
            return float(self.metadatos.get("dt", 0.0))
        return float(self.t[1] - self.t[0])

    def trayectoria(self, amplitud: float, duracion: float, inicio_ms: float = 0.0) -> dict[str, np.ndarray]:
        """Extrae y desplaza una trayectoria individual del caché.

        Parameters
        ----------
        amplitud, duracion:
            Valores que deben pertenecer exactamente a la rejilla del caché.
        inicio_ms:
            Corrimiento temporal del pulso. La trayectoria se desplaza sin resimular.
        """
        i = _indice_exacto(self.amplitudes, amplitud)
        j = _indice_exacto(self.duraciones, duracion)
        pasos = int(round(inicio_ms / self.dt))
        v_base = self.v[i, j]
        w_base = self.w[i, j]
        v = _desplazar_serie(v_base, pasos=pasos, valor_inicial=float(v_base[0]))
        w = _desplazar_serie(w_base, pasos=pasos, valor_inicial=float(w_base[0]))
        j_f = np.zeros_like(self.t)
        mascara = (self.t >= inicio_ms) & (self.t < inicio_ms + duracion)
        j_f[mascara] = amplitud
        return {"t": self.t, "v": v, "w": w, "j_f": j_f}


class AlmacenNPZ:
    """API de alto nivel para guardar y cargar cachés NPZ."""

    @staticmethod
    def guardar_cache_umbral(
        ruta: str | Path,
        resultado: ResultadoLoteUmbral,
        metadatos: dict | None = None,
        comprimido: bool = True,
    ) -> Path:
        """Guarda un resultado vectorizado en formato `.npz`."""
        ruta = Path(ruta)
        ruta.parent.mkdir(parents=True, exist_ok=True)
        metadatos = dict(metadatos or {})
        metadatos_json = json.dumps(metadatos, ensure_ascii=False)
        funcion = np.savez_compressed if comprimido else np.savez
        funcion(
            ruta,
            t=resultado.t,
            amplitudes=resultado.amplitudes,
            duraciones=resultado.duraciones,
            v=resultado.v,
            w=resultado.w,
            metadatos_json=np.array(metadatos_json),
        )
        return ruta

    @staticmethod
    def cargar_cache_umbral(ruta: str | Path) -> CacheUmbralNPZ:
        """Carga un archivo `.npz` y devuelve un objeto `CacheUmbralNPZ`."""
        ruta = Path(ruta)
        with np.load(ruta, allow_pickle=False) as datos:
            metadatos = json.loads(str(datos["metadatos_json"]))
            return CacheUmbralNPZ(
                t=datos["t"],
                amplitudes=datos["amplitudes"],
                duraciones=datos["duraciones"],
                v=datos["v"],
                w=datos["w"],
                metadatos=metadatos,
            )

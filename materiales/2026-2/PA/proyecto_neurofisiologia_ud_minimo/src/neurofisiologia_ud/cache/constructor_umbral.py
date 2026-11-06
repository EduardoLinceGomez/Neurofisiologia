"""Construcción de cachés NPZ para experimentos de umbral."""

from __future__ import annotations

from dataclasses import asdict
from pathlib import Path

from ..configuracion import RejillaUmbral
from ..integradores.integrador_ud_exponencial_rk2 import IntegradorUDBasicoExponencialRK2
from ..modelos.sistema_ud import SistemaUDBasico
from .almacenamiento_npz import AlmacenNPZ


class ConstructorCacheUmbral:
    """Coordina la generación de un caché NPZ de umbral."""

    def __init__(
        self,
        modelo: SistemaUDBasico,
        integrador: IntegradorUDBasicoExponencialRK2,
        rejilla: RejillaUmbral,
    ) -> None:
        self.modelo = modelo
        self.integrador = integrador
        self.rejilla = rejilla

    def construir(self, ruta_salida: str | Path, comprimido: bool = True) -> Path:
        """Construye el caché y lo persiste en disco."""
        resultado = self.integrador.integrar_lote_umbral(
            amplitudes=self.rejilla.amplitudes,
            duraciones=self.rejilla.duraciones,
            inicio_ms=0.0,
        )
        metadatos = {
            "modelo": "sistema_ud_basico",
            "integrador": "exponencial_para_w_y_rk2_para_v",
            "dt": self.rejilla.dt,
            "t_max": self.rejilla.t_max,
            "parametros": self.modelo.parametros.como_diccionario(),
        }
        return AlmacenNPZ.guardar_cache_umbral(
            ruta=ruta_salida,
            resultado=resultado,
            metadatos=metadatos,
            comprimido=comprimido,
        )

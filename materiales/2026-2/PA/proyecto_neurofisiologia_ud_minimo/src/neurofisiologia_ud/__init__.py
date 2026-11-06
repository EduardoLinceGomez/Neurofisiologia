"""Paquete mínimo para simulación del sistema UD-básico."""

from .configuracion import RejillaUmbral, rejilla_umbral_ejemplo
from .modelos.sistema_ud import ParametrosUDBasico, SistemaUDBasico
from .integradores.integrador_ud_exponencial_rk2 import (
    IntegradorUDBasicoExponencialRK2,
    ResultadoLoteUmbral,
    ResultadoSimulacion,
)
from .cache.almacenamiento_npz import AlmacenNPZ, CacheUmbralNPZ
from .cache.constructor_umbral import ConstructorCacheUmbral
from .analisis import AnalizadorUDBasico, ResumenPulso

__all__ = [
    "RejillaUmbral",
    "rejilla_umbral_ejemplo",
    "ParametrosUDBasico",
    "SistemaUDBasico",
    "IntegradorUDBasicoExponencialRK2",
    "ResultadoLoteUmbral",
    "ResultadoSimulacion",
    "AlmacenNPZ",
    "CacheUmbralNPZ",
    "ConstructorCacheUmbral",
    "AnalizadorUDBasico",
    "ResumenPulso",
]

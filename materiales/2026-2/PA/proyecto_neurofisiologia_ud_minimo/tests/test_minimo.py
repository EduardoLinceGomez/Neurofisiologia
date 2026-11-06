"""Pruebas mínimas de consistencia para el proyecto."""

from pathlib import Path
import tempfile

import numpy as np

from neurofisiologia_ud import (
    AlmacenNPZ,
    ConstructorCacheUmbral,
    IntegradorUDBasicoExponencialRK2,
    ParametrosUDBasico,
    SistemaUDBasico,
    rejilla_umbral_ejemplo,
)


def test_punto_fijo_reposo_y_cache() -> None:
    modelo = SistemaUDBasico(ParametrosUDBasico())
    v0, w0 = modelo.punto_fijo_reposo()
    assert -90.0 < v0 < -50.0
    assert 0.0 <= w0 <= 1.0

    rejilla = rejilla_umbral_ejemplo()
    integrador = IntegradorUDBasicoExponencialRK2(modelo=modelo, dt=rejilla.dt, t_max=rejilla.t_max)
    constructor = ConstructorCacheUmbral(modelo, integrador, rejilla)

    with tempfile.TemporaryDirectory() as carpeta:
        ruta = Path(carpeta) / "cache.npz"
        constructor.construir(ruta)
        cache = AlmacenNPZ.cargar_cache_umbral(ruta)
        assert cache.v.shape[0] == rejilla.amplitudes.size
        assert cache.v.shape[1] == rejilla.duraciones.size
        assert cache.v.shape[2] == cache.t.size
        datos = cache.trayectoria(amplitud=float(rejilla.amplitudes[0]), duracion=float(rejilla.duraciones[0]), inicio_ms=5.0)
        assert datos["v"].shape == cache.t.shape

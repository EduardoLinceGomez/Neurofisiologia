"""Script mínimo para construir un caché NPZ de umbral."""

from __future__ import annotations

from pathlib import Path

from neurofisiologia_ud import (
    ConstructorCacheUmbral,
    IntegradorUDBasicoExponencialRK2,
    ParametrosUDBasico,
    RejillaUmbral,
    SistemaUDBasico,
    rejilla_umbral_ejemplo,
)


def main() -> None:
    raiz = Path(__file__).resolve().parents[1]
    ruta_salida = raiz / "data" / "cache" / "cache_umbral_ejemplo.npz"
    modelo = SistemaUDBasico(ParametrosUDBasico())
    rejilla = rejilla_umbral_ejemplo()
    integrador = IntegradorUDBasicoExponencialRK2(
        modelo=modelo,
        dt=rejilla.dt,
        t_max=rejilla.t_max,
        tipo=rejilla.tipo,
    )
    constructor = ConstructorCacheUmbral(modelo=modelo, integrador=integrador, rejilla=rejilla)
    ruta = constructor.construir(ruta_salida)
    print(f"Caché guardada en: {ruta}")


if __name__ == "__main__":
    main()

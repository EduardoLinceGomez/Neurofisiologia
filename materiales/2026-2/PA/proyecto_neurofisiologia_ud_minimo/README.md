# Proyecto mínimo de neurofisiología: sistema UD-básico

Este proyecto implementa una versión mínima, reusable y documentada del sistema **UD-básico** de dos variables `(v, w)` descrito en tus notas. La notación sigue la formulación de los capítulos 1 y 2:

- `v` representa el potencial transmembranal.
- `w` representa la proporción de canales de la población "down" abiertos.
- `\partial_t v = J_F - J_UD(v) - J_U(v) - J_D(v, w)`.
- `\partial_t w = lpha(v) - ho(v) w`, con `ho(v) = lpha(v) + eta(v)`.

La ecuación de voltaje se interpreta como una corriente transmembranal normalizada por la capacitancia, en el espíritu de la ecuación `\partial_t v = - I_Tm / C_m` de tus notas y de la formulación clásica de conductancias de Hodgkin–Huxley.

## Decisiones numéricas

1. **`w` se integra con actualización exponencial** (Exponential Euler / Rush–Larsen de primer orden), porque su dinámica tiene la forma exacta
   `\partial_t w = lpha(v) - ho(v) w`.
2. **`v` se integra con RK2 explícito (Heun)**. Esto mantiene el código simple, estable y fácil de vectorizar.
3. **La construcción de caché usa vectorización por lotes** para recorrer una rejilla de amplitudes y duraciones sin bucles Python por trayectoria.
4. **Los resultados se guardan en `.npz` comprimido** con tensores `v[a, d, t]` y `w[a, d, t]`.

## Estructura del proyecto

```text
proyecto_neurofisiologia_ud_minimo/
├── README.md
├── pyproject.toml
├── requirements.txt
├── data/
│   └── cache/
│       └── cache_umbral_ejemplo.npz
├── notebooks/
│   └── 01_demo_sistema_ud.ipynb
├── scripts/
│   └── construir_cache_umbral.py
├── src/
│   └── neurofisiologia_ud/
│       ├── __init__.py
│       ├── configuracion.py
│       ├── estimulo.py
│       ├── analisis.py
│       ├── visualizacion.py
│       ├── modelos/
│       │   ├── __init__.py
│       │   └── sistema_ud.py
│       ├── integradores/
│       │   ├── __init__.py
│       │   └── integrador_ud_exponencial_rk2.py
│       └── cache/
│           ├── __init__.py
│           ├── almacenamiento_npz.py
│           └── constructor_umbral.py
└── tests/
    └── test_minimo.py
```

## Flujo de trabajo recomendado

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
pip install -e .
```

### 2. Construir un caché NPZ

```bash
python scripts/construir_cache_umbral.py
```

### 3. Abrir el notebook de demostración

Abre `notebooks/01_demo_sistema_ud.ipynb` en VS Code y ejecuta las celdas. El notebook únicamente importa el paquete, carga el caché y crea la figura interactiva.

## Contenido del archivo NPZ

El caché de umbral guarda:

- `t`: vector de tiempo global.
- `amplitudes`: rejilla de amplitudes del pulso.
- `duraciones`: rejilla de duraciones del pulso.
- `v`: tensor de potenciales con forma `(n_amplitudes, n_duraciones, n_t)`.
- `w`: tensor de compuertas con la misma forma.
- `metadatos_json`: metadatos serializados en JSON.

La visualización no recalcula trayectorias: selecciona una amplitud y una duración desde el caché, y para cambiar el inicio del pulso solo desplaza la trayectoria en el tiempo.

## Siguientes pasos naturales

- añadir una segunda sección para período refractario con doble pulso,
- guardar curvas adicionales (`J_F`, nullclines precalculadas, umbrales),
- extender la arquitectura al modelo de Hodgkin–Huxley completo,
- añadir pruebas más fuertes de convergencia y estabilidad.

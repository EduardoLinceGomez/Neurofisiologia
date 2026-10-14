# Neurofisiología

Repositorio de investigación para estudiar modelos compartimentales de retina.
La primera etapa desarrolla un bastón pasivo con segmento externo (O), segmento
interno (I) y terminal sináptica eléctrica (T), según el
[Issue #1](https://github.com/EduardoLinceGomez/Neurofisiologia/issues/1).

La bibliografía privada se conserva exclusivamente en `Bibliografia/`, excluida de
Git. Se documentarán referencias públicas y se distinguirán mediciones de corriente
fotosensible de potenciales simulados con parámetros ilustrativos.

La ruta de estudio prevista es bastón → cono → amacrina. Esta primera etapa se
limita al bastón; las extensiones requieren trabajo posterior.

## Qué se calcula

Se resuelven tres balances continuos de corriente con acoplamientos axiales
simétricos O-I y I-T mediante `scipy.integrate.solve_ivp`. La luz impone una
**variación** de corriente entrante negativa en O: `I_photo(t) = -Σ A_k h(t-t_k)`.
La corriente oscura de fondo no se añade como otra entrada: el equilibrio se
representa de forma idealizada mediante fugas y potenciales de reversión.

Para cada evento se usa `h(u)=(u/t_peak)^3 exp(3(1-u/t_peak))` si `u>=0`, y cero
antes. Su máximo vale uno; es una aproximación fenomenológica de cuatro etapas,
sin cascada bioquímica ni conductancias CNG dinámicas. La superposición es lineal:
el modelo no incluye saturación ni adaptación y se estudia bajo iluminación tenue.

La referencia para amplitud y tiempo al máximo es la célula 1 de **bastón de sapo**
de [Baylor, Lamb y Yau (1979)](https://doi.org/10.1113/jphysiol.1979.sp012716):
1.2 pA y 2200 ms. No se digitalizan trazas del artículo. La corriente impuesta
aproxima una variación de corriente medida; los potenciales O, I y T son
**simulaciones**, con C, g y E **ilustrativos y no calibrados**.
La terminal es únicamente un compartimento eléctrico: no hay Ca²⁺, liberación
de glutamato, sinapsis intercelulares ni potenciales de acción. Los eventos
fotónicos no son spikes neuronales.

| Magnitud | Unidad interna | Relación |
| --- | --- | --- |
| Tiempo, potencial | ms, mV | `t_peak=2.2 s=2200 ms` |
| Capacitancia total | pF | `pF*mV/ms=pA` |
| Conductancia total | nS | `nS*mV=pA` |
| Corriente entrante | pA | La variación por luz es negativa |

La derivación, interpretación y experimentos guiados están en
[el notebook](notebooks/01_baston_tres_compartimentos.ipynb).
La procedencia de cada valor está en
[referencias y parámetros](docs/referencias_y_parametros.md).

## Instalación y reproducción

Se requiere Python 3.11 o posterior. Desde la raíz del repositorio:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[dev,widgets]'
python -m ipykernel install --user --name neurofisiologia --display-name 'Neurofisiología (.venv)'
python -m pytest -q
python scripts/execute_notebook.py --kernel neurofisiologia
python scripts/verify_notebook_controls.py --kernel neurofisiologia
MPLBACKEND=Agg python -m neurofisiologia.examples
jupyter lab notebooks/01_baston_tres_compartimentos.ipynb
```

`widgets` es opcional; `.[dev]` basta para ejecutar pruebas y notebook.
Sin widgets, las comparaciones se hacen llamando la función de la celda.
En VS Code, abrir el notebook y seleccionar el kernel **Neurofisiología (.venv)**.
La celda de parámetros permite cambiar las tres C, fugas, reversión y ambos
acoplamientos; los controles opcionales comparan amplitud, acoplamiento y tasa
de eventos efectivos, con semilla fija.

El notebook fuente permanece sin salidas. Su versión ejecutada y las cuatro
figuras de verificación se guardan en `outputs/`, ignorado por Git. El script
ejecuta desde la raíz aunque se invoque desde otro directorio. GitHub Actions
repite las pruebas, ejecuta el notebook y genera figuras en Linux.

## Uso del modelo desde Python

```python
from dataclasses import replace
import numpy as np
from neurofisiologia import RodParameters, PhotonEvents, simulate

p = replace(RodParameters(), g_oi_ns=0.2, g_it_ns=0.05)
events = PhotonEvents.from_times([1000, 4000, 6500], amplitude_pa=1.2)
result = simulate(np.linspace(0, 16000, 801), p, events)
print(result.voltage_mv[:, -1])  # orden O, I, T; mV
```

`dark_equilibrium(p)` calcula el reposo también si los tres E difieren.
Los estímulos Poisson usan un generador local con semilla explícita; su tasa
está en eventos efectivos por segundo, no fotones incidentes por área.
Iniciar la integración antes del primer evento o proporcionar un estado inicial
calculado previamente: la función no reconstruye la historia anterior al inicio.
La malla de salida y el paso adaptativo son diferentes; el paso interno está
limitado por `t_peak/30` y puede reducirse con `max_step_ms`.

## Revisar seguridad y cambios

```bash
git remote -v
git status --short --ignored
git check-ignore -v Bibliografia/ Bibliografia/jphysiol00752-0614.pdf
git ls-files -- Bibliografia/
git rev-list --objects --all -- Bibliografia/
git diff main...HEAD --stat
git diff main...HEAD -- src/ tests/ docs/
```

Los dos comandos que enumeran contenido de Git para `Bibliografia/` deben dar
salida vacía. `.venv/`, `outputs/` y la bibliografía se conservan localmente.
Consultar [validación](docs/validacion.md) para la evidencia de esta entrega.

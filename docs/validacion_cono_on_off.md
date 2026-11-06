# Validación de M0: Cono → Bipolar ON/OFF

## Alcance y reproducción

Implementación del [Issue #7](https://github.com/EduardoLinceGomez/Neurofisiologia/issues/7),
en la rama `feat/retina-cone-bipolar-on-off-m0`, creada directamente desde `main`
(`001eae1ad282cb183d520de0f2a9c10811fbd8f3`). El PR #6 se comprobó abierto,
en borrador y no fusionado al iniciar; M0 no incorpora sus commits ni modifica
sus materiales históricos. No se leyó ni alteró `Bibliografia/`; continúa
ignorada y sin archivos rastreados.

Entorno local: Python 3.12.14, NumPy 2.5.4, SciPy 1.18.1, Matplotlib 3.11.2,
ipywidgets 8.1.9. No se añadieron dependencias. Desde la raíz, con el entorno
instalado según el README:

```bash
source .venv/bin/activate
MPLBACKEND=Agg python -m pytest -q
MPLBACKEND=Agg python scripts/execute_notebook.py --kernel neurofisiologia
MPLBACKEND=Agg python scripts/verify_notebook_controls.py --kernel neurofisiologia
MPLBACKEND=Agg python scripts/execute_m0_notebook.py --kernel neurofisiologia
MPLBACKEND=Agg python scripts/verify_m0_controls.py --kernel neurofisiologia
MPLBACKEND=Agg python scripts/verify_circuit_figures.py
MPLBACKEND=Agg python -m neurofisiologia.examples
jupyter lab notebooks/03_cono_bipolares_on_off.ipynb
```

## Evidencia física y numérica

La suite completa contiene **160 pruebas: 115 anteriores y 45 nuevas**, todas
aprobadas. Las nuevas comprueban:

- Parámetros finitos, C/fugas/pendiente/ganancia positivas, máximos sinápticos
  no negativos, L≥0, fondo positivo e intervalos no solapados.
- Unidades contrastadas con un balance independiente en SI; r acotada y
  creciente; g_ON decreciente y g_OFF creciente, ambas no negativas.
- Equilibrio cerrado y RHS≈0, también con parámetros asimétricos y otro L0.
- Cadena causal completa para contrastes ±0.1, ±0.5 y ±1; recuperación posterior
  al pulso y a un tren, valores finitos y determinismo.
- La luz cambia inicialmente solo la derivada del cono; las dos corrientes
  sinápticas son entrantes en el ejemplo aunque sus **variaciones** sean opuestas.
  El signo contrario no se aplica a los voltajes ni a la RHS como factor artificial.
- Desconexión selectiva de cada sinapsis sin afectar al cono ni a la otra rama.
  Con parámetros bipolares asimétricos se conservan los signos, sin exigir
  amplitudes especulares.
- Solución RC exacta del cono y de ambas bipolares con conductancias constantes.
  Un pulso de 0.01 ms entre muestras se integra y no desaparece por usar una
  malla de salida gruesa. Se separan todos los saltos de iluminación.
- Cambiar C modifica el tiempo sin cambiar equilibrio; ganancia y fugas modifican
  las amplitudes según las ecuaciones. El máximo bipolar puede seguir al del cono.
- Cada curva causal contiene exactamente la variable correspondiente del modelo;
  referencia fija y modificación usan estilos distintos y sus propios reposos.
  Polaridad de fuentes negativa/positiva/cero, rama desconectada, rótulos dentro
  del lienzo sin colisiones y leyendas fuera de los ejes de la cadena causal.

Con valores canónicos y pasos de ±0.5 entre 100 y 300 ms, la simulación produce:

| Cambio de luz | Extremo ΔV_C | Extremo ΔV_ON | Extremo ΔV_OFF |
| --- | ---: | ---: | ---: |
| Incremento | −4.9998 mV | +4.0583 mV | −4.8788 mV |
| Decremento | +4.9998 mV | −4.8788 mV | +4.0583 mV |

Son extremos calculados durante el protocolo, **no mediciones**. El reposo es
(−40, −48, −48) mV, r*=0.5 y g_ON*=g_OFF*=0.25 nS. Los signos se deducen de
`dr/dV_C>0`, `dg_ON/dr<0`, `dg_OFF/dr>0` y `dV_b_equilibrio/dg>0`.
Todas las constantes son ilustrativas y no calibradas.

## Notebooks e interacción

- Notebooks del bastón: 01 (9 celdas de código) y 02 (17), ejecutados completos;
  cuatro variantes de controles/fallback y ejemplos previos sin errores.
- Notebook M0: 11 celdas de código ejecutadas completas. Además se repite con
  widgets y con ausencia de widgets forzada, con una celda adicional de aceptación
  en cada copia ejecutada. No se modifica la fuente para estas comprobaciones.
- Contrastes 0, 0.25 y 1; los nueve parámetros a factor 2; restauración a factor 1.
  Se comprueban valores y resultados de los callbacks, finitud, signos, entrada
  idéntica, independencia de la referencia canónica y reposos propios.
- `execute_m0_notebook.py` rechaza errores de celdas **y de estados de widgets**,
  fuentes con salidas y ejecuciones sin al menos nueve imágenes PNG embebidas.
  El backend inline se registra explícitamente incluso con `MPLBACKEND=Agg`.
- Los tres notebooks fuente permanecen limpios, sin salidas ni rutas personales.
  Se comprobó por SHA-256 que los 15 archivos anteriores rastreados en `src/`,
  `tests/` y `notebooks/` permanecen idénticos a la base.

La CI repite la suite completa, notebooks 01/02/03, controles con y sin widgets,
auditoría previa de circuitos, ejemplos y frontera de bibliografía. Conserva
`outputs/` como artefacto `notebook-y-figuras`; no versiona productos generados.
La comprobación de callbacks usa kernels reales mediante nbclient. La auditoría
manual de lectura usa el HTML ejecutado; no equivale a una prueba manual de todos
los controles en cada versión de JupyterLab, VS Code o navegador.

## Auditoría visual y pedagógica

Se revisaron los renders de los esquemas y experimentos, y la lectura del
notebook ejecutado. La revisión comprueba signos, escalas comparables, unidades,
leyendas, reposos, polaridades y que la explicación preceda al código necesario
para experimentar. Se corrigieron el rótulo exterior del circuito, las leyendas
que podían ocultar recuperaciones y la ausencia de imágenes embebidas bajo Agg.

La ruta didáctica presenta primero potencial graduado y contraste respecto a L0;
luego balance del cono, liberación, OFF, ON y reposo. Pregunta y predicción
preceden a cada experimento; interpretación, tabla causal, balance de corrientes,
calibración y respuestas plegadas permiten leer los mecanismos sin inspeccionar
el integrador. La figura 6.15 y la explicación de receptores se verificaron en
las páginas 247/251 de una copia pública; véase la [procedencia](referencias_cono_on_off.md).

Los siguientes archivos se regeneran en `outputs/retina_on_off/`, cada uno en
**PNG y SVG**:

| Prefijo | Contenido y comprobación visual |
| --- | --- |
| `M0_01_fisiologia` | Una señal química común, receptores distintos, tres células |
| `M0_02_circuitos` | Un RC por célula; fuentes correctas y sin cable intercelular |
| `M0_03_cono` | Luz y corriente por pasos; voltaje continuo con signos correctos |
| `M0_04_transferencia` | r creciente; dos dependencias opuestas de g≥0 |
| `M0_05_fondo` | Equilibrio sin transitorio artificial |
| `M0_06_cadena` | Incremento/decremento juntos, siete filas y escalas compartidas |
| `M0_07_pulsos` | Retorno al fondo, relajación y respuestas graduadas sucesivas |
| `M0_08_aislamiento` | Solo desaparece la respuesta de la sinapsis desconectada |
| `M0_09_sensibilidad` | Doble C_ON, referencia fija discontinua y retardo sin cambio de reposo |

Se pueden exportar las salidas para lectura estática:

```bash
jupyter nbconvert --to html --template lab --output M0_lectura \
  --output-dir outputs/retina_on_off \
  outputs/retina_on_off/03_m0_con_widgets.executed.ipynb
```

El HTML muestra los resultados guardados; para recalcular controles hace falta
el kernel del notebook. La validación científica aquí es del modelo acordado y
sus consecuencias, no una calibración biológica ni una prueba de aprendizaje con
estudiantes. La aceptación docente permanece para revisión del PR en borrador.

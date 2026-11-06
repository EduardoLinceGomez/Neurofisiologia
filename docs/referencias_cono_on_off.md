# Fuentes y procedencia de M0

Consulta pública: 6 de noviembre de 2026. No se abrió, leyó, copió ni modificó
`Bibliografia/`. Las fuentes públicas de consulta y sus renders quedan locales
en `outputs/retina_on_off/`; ningún PDF o figura del libro se versiona.

## Referencia principal: Sterling y Demb

Sterling, P. y Demb, J. B. (2004). *Retina*, capítulo 6 de *The Synaptic
Organization of the Brain*, 5.ª edición, G. M. Shepherd (ed.), pp. 217–270.
[Registro editorial y DOI](https://doi.org/10.1093/acprof:oso/9780195159561.003.0006).
[Copia pública alojada en NYU](https://www.cns.nyu.edu/csh/csh06/PDFs/SterlingDemb2004.pdf).

Se inspeccionaron visualmente las páginas impresas **247 (figura 6.15)** y
**251 (iGluR/mGluR6)**: páginas PDF 31 y 35, contando desde uno. La figura
motiva el contraste respecto al fondo y la separación de respuestas ON/OFF.
El texto explica que glutamato reduce indirectamente una apertura catiónica ON,
mientras la rama OFF usa receptores ionotrópicos. No debe confundirse el cierre
de una entrada despolarizante con abrir una conductancia inhibitoria de Cl⁻.

Es una exposición de circuitos retinianos; la figura es una síntesis fisiológica,
no un conjunto de registros que hayamos digitalizado para ajustar M0. No asignamos
una especie ni importamos números de sus trazas. El capítulo no especifica
nuestros C, fugas, k_L, sigmoide o máximos sinápticos. Los diagramas nuevos son
originales y muestran únicamente el alcance autorizado, sin copiar la figura.

## Evidencia primaria complementaria

- [Vardi, Duvoisin, Wu y Sterling (2000)](https://pubmed.ncbi.nlm.nih.gov/10870081/),
  *Localization of mGluR6 to dendrites of ON bipolar cells in primate retina*.
  J. Comp. Neurol. 423:402–412. Resumen público: inmunomarcaje en mono, gato y
  conejo, localización dendrítica de mGluR6. Apoyo anatómico, sin parámetros
  transferidos ni cuantificación de nuestras conductancias.
- [Morgans et al. (2009)](https://pmc.ncbi.nlm.nih.gov/articles/PMC2776419/),
  *TRPM1 is required for the depolarizing light response in retinal ON-bipolar
  cells*. PNAS 106:19174–19178, DOI 10.1073/pnas.0908711106.
  Ratón; resultados de knockout/patch clamp en bipolares (sección de resultados
  sobre la corriente acoplada a mGluR6). Apoya el papel de TRPM1 en la respuesta
  ON; no se usan sus valores para calibrar M0. Esta evidencia es **posterior a
  2004**: no atribuimos al capítulo la identificación molecular posterior.

## Qué es fuente, hipótesis y consecuencia

| Elemento | Estatuto en M0 |
| --- | --- |
| Distinción ON/OFF, receptores y signo respecto al fondo | Motivación fisiológica de las fuentes anteriores |
| Tres células, un voltaje por célula | Reducción acordada en el [Issue #7](https://github.com/EduardoLinceGomez/Neurofisiologia/issues/7) |
| I_foto = −k_L(L−L0) | Hipótesis fenomenológica del Issue; no fototransducción completa |
| r sigmoidal instantánea, g_ON∝1−r y g_OFF∝r | Hipótesis algebraicas del Issue; no curvas medidas de receptores |
| Equilibrio ponderado, signos y tiempos RC | Consecuencias matemáticas de las ecuaciones implementadas |
| Todas las trazas y figuras M0 | Simulaciones con constantes ilustrativas, no registros experimentales |

## Parámetros iniciales y unidades

**Todos los valores siguientes son elecciones didácticas nuestras, sin especie
asignada ni calibración.** No proceden de Baylor ni del ajuste a otra célula.

| Campo del código | Valor | Unidad | Función |
| --- | --- | --- | --- |
| `capacitance_pf` (C, ON, OFF) | 20, 30, 30 | pF | Almacenamiento total por célula |
| `leak_ns` | 1, 1, 1 | nS | Fuga; mantiene estabilidad y un equilibrio definido |
| `leak_reversal_mv` | −40, −60, −60 | mV | Reversiones efectivas, no reposos bipolares |
| `synaptic_reversal_mv` (ON, OFF) | 0, 0 | mV | Reversión catiónica por encima del reposo |
| `g_on_max_ns`, `g_off_max_ns` | 0.5, 0.5 | nS | Máxima apertura efectiva de cada rama |
| `light_gain_pa` | 10 | pA/u. L | Ganancia de variación de corriente |
| `release_half_mv` | −40 | mV | Voltaje de r=1/2 |
| `release_slope_mv` | 5 | mV | Anchura de la sigmoide |
| L0, ΔL de ejemplo | 1, ±0.5 | Adimensional | Fondo no nulo y contraste controlado |
| Paso de ejemplo | [100,300) | ms | Protocolo, no latencia fisiológica medida |

El reposo calculado es (−40, −48, −48) mV; r*=0.5 y ambas g*=0.25 nS.
Los tiempos basales son 20, 24 y 24 ms. Estas cifras se **deducen de las
hipótesis** y no se presentan como mediciones de un cono o bipolar real.

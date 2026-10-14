# Referencias y procedencia de parámetros

## Referencia experimental de fotocorriente

Baylor, D. A., Lamb, T. D. y Yau, K.-W. (1979). *Responses of retinal rods to
single photons*. Journal of Physiology, 288, 613-634.
[DOI y artículo](https://doi.org/10.1113/jphysiol.1979.sp012716).
[Copia pública del artículo alojada en NYU](https://www.cns.nyu.edu/csh/csh06/PDFs/Baylor1979.pdf).

Se estudian segmentos externos de **bastones de sapo**, mediante electrodo de
succión. No son registros de conos, humanos ni del potencial de la terminal.

| Referencia | Valor | Localizador | Uso |
| --- | --- | --- | --- |
| Amplitud ajustada, célula 1 | 1.2 pA | Tabla 1, p. 621; fig. 3A/B, p. 618; ajuste explicado en p. 620 | Amplitud de evento predeterminada |
| Tiempo al máximo, célula 1 | 2.2 s = 2200 ms | Fig. 4 y leyenda, p. 619 | Tiempo al máximo del núcleo |
| Media de amplitudes, ocho células | 0.96 pA | Tabla 1, fila Mean, p. 621 | Contexto experimental; no sustituye célula 1 |
| Promedio de σ₁, ocho células | 0.20 pA | Tabla 1, columna σ₁, p. 621 | Dispersión de eventos dentro de cada célula, promediada |

**Precisión estadística:** 0.20 pA no es el error estándar de 0.96 pA ni la
desviación entre las ocho amplitudes medias. No se usa aquí para sortear A.
Cada evento tiene amplitud fija salvo modificación explícita del usuario.

El signo negativo aplicado a A expresa nuestra convención de corriente entrante:
la luz reduce la corriente fotosensible respecto de oscuridad. No reproduce la
polaridad gráfica del electrodo. La forma normalizada `u³ exp(-3u/t_peak)` es
fenomenológica; la referencia a cuatro etapas procede del ajuste `n=4` de la
fig. 4, sin asignar etapas moleculares. No se ajustó la curva al registro.

## Parámetros eléctricos ilustrativos, no calibrados

| Nombre en Python | Valor inicial | Unidad | Procedencia / función |
| --- | --- | --- | --- |
| `capacitance_pf` | O=20, I=15, T=5 | pF | Elección didáctica; almacenamiento de carga |
| `leak_ns` | O=0.05, I=0.10, T=0.05 | nS | Elección didáctica; fuga local |
| `reversal_mv` | O=I=T=-40 | mV | Referencia idealizada de oscuridad |
| `g_oi_ns` | 0.10 | nS | Elección didáctica; conexión O-I simétrica |
| `g_it_ns` | 0.10 | nS | Elección didáctica; conexión I-T simétrica |

Todos son valores **totales** por compartimento, no densidades. No se dedujeron
de la geometría del bastón ni de Baylor. Las C y fugas deben ser positivas; los
acoplamientos admiten cero. Esta restricción asegura un equilibrio oscuro único.
Si E difiere entre compartimentos, el reposo se calcula resolviendo el sistema
lineal; no se inicializa cada V simplemente en su propio E.

Las tasas Poisson (0.3 eventos/s por defecto), tiempos definidos, semilla 2026,
ventana y factores de comparación son decisiones de experimento numérico. La
tasa describe respuestas elementales efectivas, sin eficiencia cuántica,
área colectora, flujo óptico calibrado ni ruido oscuro.

## Marco del balance compartimental

Herrera-Valdez, M. A. (2026). *Action Potential Thresholds and Excitability from
the Geometry of Membrane Potential*. Preprint bioRxiv, versión 1 publicada el
26 de agosto de 2026.
[DOI](https://doi.org/10.64898/2026.08.21.746364).
[PDF público v1](https://www.biorxiv.org/content/10.64898/2026.08.21.746364v1.full.pdf).

La sección 3.8, p. 18, **ecuación 38** presenta el balance con vecinos en la
**versión pública de agosto** consultada. En ella la ecuación 36 (sección 3.7,
p. 17) describe curvatura. La [decisión aprobada](decisiones/0001-laboratorio-estudio-baston.md)
y la revisión del PR #2 reportan una **versión de estudio fechada 1 de septiembre
de 2026**, sección 3.6, **ecuación 36**, para el balance multicompartmental.
Este segundo localizador procede de la documentación aportada; no se revalidó
abriendo un PDF privado y no se inventa una página para esa versión.
Son ediciones diferentes; no se intercambian sus números de ecuación. Las EDO
implementadas siguen siendo las tres del Issue. Al normalizar cada balance por C_j, `g_jk/C_j` puede ser distinto de
`g_jk/C_k`; la **conductancia y la corriente axial**, antes de dividir por C,
son simétricas e iguales y opuestas.

Hodgkin, A. L. y Huxley, A. F. (1952). *A quantitative description of membrane
current and its application to conduction and excitation in nerve*. Journal of
Physiology, 117, 500-544.
[DOI](https://doi.org/10.1113/jphysiol.1952.sp004764).
Referencia histórica de balance capacitivo y corrientes de membrana; no se
trasladan sus canales activos ni sus parámetros al bastón pasivo.

## Alcance y reproducibilidad

Las referencias públicas se consultaron el 14 de octubre de 2026. Se revisaron
visualmente las páginas 619-621 de Baylor y la p. 18 de Herrera-Valdez v1; los
PDF públicos y extracciones de consulta se mantuvieron fuera del repositorio.
No se abrieron los documentos de `Bibliografia/` para investigación ni se
cargaron a servicios externos; solo se calculó su huella local de integridad.
El notebook y las figuras usan curvas generadas, sin copiar tablas completas,
imágenes del artículo ni trazas experimentales digitalizadas.

Una corriente de referencia no determina por sí sola C, fugas y acoplamientos.
Por eso no se infiere una predicción cuantitativa de voltaje real ni actividad
sináptica. La superposición lineal pierde validez bajo iluminación intensa al
omitir saturación, adaptación y retroalimentación. Estas extensiones, así como
conos y amacrinas, quedan para etapas posteriores.
## Fuentes del contexto fisiológico (sin calibración nueva)

| Fuente pública | Especie / localizador | Concepto o variable | Uso en el laboratorio |
| --- | --- | --- | --- |
| [Hagins, Penn y Yoshikami (1970), Dark current and photocurrent in retinal rods](https://pubmed.ncbi.nlm.nih.gov/5439318/) | Rata; Biophys. J. 10:380-412; resumen público | Corriente oscura y reducción por luz | Motivación del signo; ninguna cifra eléctrica importada |
| [Yau y Nakatani (1985), Light-suppressible, cyclic GMP-sensitive conductance](https://pubmed.ncbi.nlm.nih.gov/2995816/) | Sapo Bufo marinus (MeSH); Nature 317:252-255; resumen | Conductancia de membrana sensible a luz/cGMP | Contexto experimental del cierre fotosensible; sin g calibrada |
| [Purves et al., Neuroscience, Phototransduction](https://www.ncbi.nlm.nih.gov/books/NBK10806/) | Contexto de vertebrados; fig. 11.6 y 11.7 | Pigmento, transducina, PDE, cGMP y canales | Secuencia cualitativa; no dato cuantitativo de este modelo |
| [Webvision, Photoreceptors](https://www.ncbi.nlm.nih.gov/books/NBK11522/) | Anatomía comparada, énfasis en primates; Light microscopy, fig. 5 | Segmentos y terminal | Anatomía; sin convertir dimensiones de otras especies en C/g |

La corriente contextual tiene unidades de A/pA y la conductancia S/nS, pero
no se importan valores de esas fuentes. El mecanismo real se explica como
antecedente de la entrada impuesta, no se añade al sistema. El mapa de regiones
es vectorial original, conceptual y no a escala; no copia figuras de artículos.

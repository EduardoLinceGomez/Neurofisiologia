# Validación del laboratorio pedagógico (Issue #3)

## Correcciones de la auditoría independiente del PR #5

Se leyó íntegramente la revisión publicada sobre `3b02554` antes de editar.
El árbol de trabajo estaba limpio. Esta revisión se limita a `plot_circuit`,
pruebas y evidencia de validación; las fuentes de ambos notebooks y la
documentación pedagógica anterior se conservan. La base del PR sigue siendo
`docs/estudio-pedagogico-baston`, en borrador, sin merge ni auto-merge.

### Hallazgos y representación corregida

1. **Polaridad de E (F1/F5).** Se sustituyó la batería por una fuente ideal
   circular. Para E<0, la terminal superior lleva − y la inferior +; para
   E>0, al revés. Para E=0 se muestra 0, sin polaridad. La terminal inferior
   está conectada a la referencia exterior de 0 mV; el potencial de la superior
   respecto de esa referencia es E. La etiqueta E incluye mV y se distingue
   explícitamente del potencial instantáneo V del nodo, separado por la fuga.
2. **Fotocorriente (F5).** Se retiraron su flecha magenta y el cable que podía
   sugerir un flujo absoluto de iones. Un recuadro independiente identifica
   la contribución algebraica al balance de O, la convención entrante positiva
   y su significado: variación de corriente entrante de oscuridad, sin afirmar
   flujo iónico absoluto hacia fuera. F1 muestra la fórmula; F5, el valor
   firmado calculado, incluida la entrada nula. Las únicas flechas restantes
   son axiales, rojas y orientadas por su signo efectivo; F1 declara su
   orientación de referencia. Se conserva el umbral gráfico de 10⁻¹⁰ pA.
3. **Composición (F1/F5).** Se reservan zonas distintas para entrada, resultados
   por nodo, acoplamientos, ramas C/fuga/E, exterior y línea temporal. Los
   símbolos de fuente son circulares, con escala de ejes igual. Los rótulos
   del diagrama usan 11–16 puntos, sin reducirlos para ocultar colisiones.
   C/g/E y acoplamientos están rotulados y declarados constantes, ilustrativos
   y no calibrados; el circuito equivalente no representa anatomía a escala.
   La prueba de límites detectó inicialmente desbordamiento de `gL=0.123456`
   en T: se amplió el margen lateral y la regresión ahora pasa.

Dos detalles directamente relacionados se corrigieron también: g axial=0
se dibuja como conexión abierta, sin flecha; y una corriente pequeña no nula
se rotula en notación científica, para evitar una flecha junto a un aparente
`0.000 pA`. El cero exacto se muestra sin signo, incluido −0 de punto flotante.
Estas decisiones afectan solo a la representación, no a las corrientes calculadas.

### Comprobaciones reproducibles

- **115 pruebas aprobadas**, incluidas las 77 existentes; 38 casos nuevos
  verifican polaridad y posición de símbolos para E negativos/positivos/nulos,
  fotocorriente algebraica negativa/nula, sentidos axiales positivos/negativos,
  ausencia de flechas bajo el umbral y conexiones abiertas. Se comprueban
  intersecciones entre cajas de texto, recuadro de entrada dentro del eje y
  títulos/pies dentro de la figura en 16 combinaciones de parámetros/instante.
  Es una regresión geométrica básica: no sustituye inspección visual.
- Ambos notebooks completos: **9 y 17 celdas de código**, respectivamente.
  Los cuatro casos de controles (01/02, con/sin widgets) se ejecutaron sin
  errores de celda, incluidos tiempo, parámetros avanzados y reinicio.
  La comprobación de callbacks no equivale a una prueba manual en VS Code.
- **F1 y F5 regeneradas en PNG y SVG** mediante el notebook 02; además,
  `scripts/verify_circuit_figures.py` guarda **16 PNG y 16 SVG** de auditoría
  en `outputs/auditoria_circuito/`. La CI ejecuta también este generador y
  publica sus archivos en el artefacto `notebook-y-figuras`.
- Matriz de auditoría: E=(−40,−40,−40), (+40,+40,+40), (0,0,0) y el caso
  mixto E=(−123.456,+12.3456,0) mV; este último usa
  C=(200,0.5,123.456) pF, gL=(0.001,2,0.123456) nS,
  gOI=0 y gIT=1.23456 nS. Misma entrada: evento a 1000 ms, A=1.2 pA,
  pico=2200 ms; F1 estática y F5 en 0, 3440 y 12000 ms. E positivos/cero
  sirven para comprobar la convención eléctrica, no como valores fisiológicos.
- Inspección visual de PNG y SVG renderizados en navegador: fuentes, signos,
  muestra de 3440 ms, fotocorriente nula antes del evento, reversión positiva,
  nula y mixta, rótulos largos y conexión abierta. No se observaron colisiones
  ni recortes en las vistas revisadas. Las variantes automáticas cubren más
  combinaciones que esa inspección visual.
- Los SHA-256 de `model.py`, `parameters.py`, `stimulus.py`, `analysis.py`,
  las referencias y los dos notebooks fuente no cambiaron. Cuatro simulaciones
  (individual, E distintos, Poisson y desacoplado) se compararon con un registro
  tomado antes de las correcciones: voltajes **idénticos bit a bit**. Las tres
  EDO, integrador, tolerancias, valores iniciales y datos de Baylor no cambian.
- `Bibliografia/` no se abrió, leyó, movió, copió ni modificó. Conforme a esta
  restricción, **no se repitieron los hashes de archivos privados**. Se comprobaron
  únicamente ignore, índice e historial de Git: no contienen archivos de esa
  carpeta. `outputs/` continúa ignorado y sin archivos rastreados.

```bash
source .venv/bin/activate
python -m pytest -q
MPLBACKEND=Agg python scripts/execute_notebook.py --kernel neurofisiologia
MPLBACKEND=Agg python scripts/verify_notebook_controls.py --kernel neurofisiologia
python scripts/verify_circuit_figures.py
open outputs/estudio_baston/F1_circuito.png outputs/estudio_baston/F5_estado_temporal.png
open outputs/estudio_baston/F1_circuito.svg outputs/estudio_baston/F5_estado_temporal.svg
git check-ignore -v Bibliografia/ outputs/
git ls-files -- Bibliografia/ outputs/
git log --all --oneline -- Bibliografia/
```

## Registro de entrega inicial: estudio guiado

Comprobaciones locales del 14 de octubre de 2026, con el mismo entorno Python
3.12.14 documentado abajo. Se conservó la decisión 0001 y el plan 02 sin cambios.
La rama `feat/rod-guided-study` parte de `origin/docs/estudio-pedagogico-baston`;
su PR en borrador se dirige a esa rama documental, conservando la revisión por etapas.

- **77 pruebas aprobadas**, incluidas las 49 originales. La última corrida
  completa local terminó en 5.65 s; las comprobaciones de figuras y contrato
  se repitieron tras ajustar presentación y metadatos, sin fallos.
- **Ambos notebooks completos**, sin errores: 01 con 9 celdas de código;
  02 con 55 celdas, 17 de código y etapas 00–15. Fuentes sin salidas ni
  cuentas de ejecución. La preparación y configuración de widgets del 02
  pueden plegarse en frontends que respeten esos metadatos.
- **Cuatro variantes de validación**: ambos notebooks con callbacks de widgets
  y con importación de widgets deshabilitada. El 01 añade una celda con cinco
  comparaciones; el 02 añade una celda que comprueba A, tasa, pico, semilla,
  las tres C/fugas/E, ambos acoplamientos, tiempo, V/ΔV y reinicio.
- Se prueba específicamente que variar solo A cambia corriente y voltaje,
  conserva los tiempos y no cambia la referencia; variar solo tasa conserva
  referencia y A pero cambia el tren/corriente/resultado representados.
- Cuatro escenarios (individual, E distintos, Poisson y desacoplado) dieron
  voltajes **idénticos bit a bit** a un registro local de la implementación
  anterior, guardado fuera de Git. La integración y valores iniciales no cambian.
- El desglose se recompone por nodo, sus axiales suman cero y coincide con
  el lado derecho matricial que integra el solver en todas las muestras probadas.
- `solve_ivp` frente a exponencial matricial y cuadratura independientes:
  diferencia máxima **1.41 × 10⁻⁸ mV** en el experimento del notebook 02.
  La identidad de variación de constantes es analítica; ambas evaluaciones
  de curvas son numéricas. Al limitar el paso a 5 ms: **1.94 × 10⁻⁸ mV**.
- **13 SVG y 13 PNG** generados localmente: F1–F8, anatomía conceptual, RC
  analítico, pareja O-I y dos comparaciones. Se revisaron ejes, unidades,
  rótulos, leyendas, signos, textos y condiciones. En F5 se enlaza el instante
  con V(t), se invierte la flecha según el signo y no se dibuja si I es cero.
- Revisión adicional en navegador del HTML de lectura generado por nbconvert:
  deducción RC y matriz/variación de constantes renderizadas; respuestas plegadas
  inicialmente ocultas y apertura comprobada; descripciones de imágenes y
  preparación omitida en esa vista de lectura. Ese HTML es evidencia estática,
  no otro simulador; la interactividad requiere el kernel del notebook.

### Auditoría adversarial realizada

| Perspectiva | Fallo que se buscó | Evidencia / resolución |
| --- | --- | --- |
| Científica | Confundir corriente medida con V simulado; importar otra especie; añadir mecanismos | Cuatro categorías visibles, tabla de fuentes, parámetros originales; ningún canal/estado nuevo |
| Matemática | Cambiar signos, simetría o equilibrio; inventar retrasos nulos | Desglose probado contra matriz; E distintos; métricas NaN/None; prueba de K positiva y modos |
| Numérica | Saltar eventos, perder superposición o reproducibilidad | 49 pruebas conservadas, referencia independiente, cuatro regresiones idénticas, semillas locales |
| Comparaciones | Referencia que sigue A/tasa; atribuir azar a tasa | Entradas separadas, regresiones específicas, trenes y ensemble de 12 realizaciones por tasa |
| Visual | Cable ideal en lugar de g axial; signos falsos; ejes temporales incompatibles | Resistencias dibujadas, flechas firmadas/ausentes, ejes compartidos, límites y ticks legibles |
| Pedagógica | Suponer fisiología, adelantar matrices, ocultar significado en código | Anatomía/mecanismo/vocabulario primero; balances 1→2→3; preguntas, predicciones, interpretación y soluciones |
| Privacidad | Bibliografía o salidas en Git | Cinco SHA-256 idénticos, ignore confirmado, índice/historial revisados; salidas locales ignoradas |

La auditoría anterior es una revisión del agente implementador con pruebas y
evidencia visual; no sustituye revisión científica humana independiente. Los
callbacks y alternativas Python se comprobaron, pero no se hizo una prueba manual
de widgets dentro de VS Code. La lectura HTML sí se inspeccionó en navegador.
La numeración de Herrera-Valdez de septiembre procede de la documentación
aprobada y se distingue de la pública de agosto; no se abrió el PDF privado.
Las C/g/E siguen **ilustrativas y no calibradas**: el laboratorio no predice
liberación de glutamato ni voltajes reales cuantitativos.

### Reproducir y revisar

```bash
source .venv/bin/activate
python -m pytest -q
MPLBACKEND=Agg python scripts/execute_notebook.py --kernel neurofisiologia
MPLBACKEND=Agg python scripts/verify_notebook_controls.py --kernel neurofisiologia
MPLBACKEND=Agg python -m neurofisiologia.examples
git check-ignore -v Bibliografia/ outputs/
git ls-files -- Bibliografia/ outputs/
git log --all --oneline -- Bibliografia/
git diff origin/docs/estudio-pedagogico-baston...HEAD --stat
```

Los dos comandos que enumeran archivos/commits bibliográficos deben quedar vacíos.
`git rev-list --objects --all -- Bibliografia/` puede mostrar un objeto árbol raíz
sin nombre en esta versión de Git: no es un archivo bibliográfico. Se inspeccionaron
los árboles completos de todas las revisiones y no contienen `Bibliografia/`.
Los productos quedan en `outputs/`, ignorados; CI ejecuta pruebas, ambos notebooks,
cuatro variantes de controles, ejemplos y exclusión de bibliografía.

## Registro histórico: implementación del Issue #1

Comprobaciones locales del 14 de octubre de 2026, en el directorio existente,
con macOS y Python 3.12.14. El commit de implementación se identifica en el PR;
esta nota registra los comandos y resultados reproducibles.

## Entorno comprobado

| Paquete | Versión local |
| --- | --- |
| NumPy | 2.5.4 |
| SciPy | 1.18.1 |
| Matplotlib | 3.11.2 |
| pytest | 9.1.1 |
| nbclient | 0.11.0 |
| nbformat | 5.11.1 |
| ipywidgets (opcional) | 8.1.9 |

`python -m pip check` no encontró incompatibilidades. `pyproject.toml` define
rangos compatibles; esta tabla describe la ejecución local y no congela todo
el entorno de futuras instalaciones.

## Pruebas y notebook

```bash
source .venv/bin/activate
python -m pytest -q
MPLBACKEND=Agg python scripts/execute_notebook.py --kernel neurofisiologia
MPLBACKEND=Agg python scripts/verify_notebook_controls.py --kernel neurofisiologia
MPLBACKEND=Agg python -m neurofisiologia.examples
```

- **49 pruebas aprobadas**, última ejecución local en 0.76 s. Se comprueban
  reposo, E distintos, signo y causalidad, desacoplamiento, efecto del
  acoplamiento, cancelación axial, unidades SI, superposición, determinismo,
  estadísticas Poisson y rechazo de entradas inválidas.
- Dos referencias independientes verifican la integración: convolución de
  un RC desacoplado y exponencial matricial para relajación pasiva acoplada.
  Un evento breve tardío se detecta incluso con salida escasa.
- **Notebook completo sin errores:** 20 celdas, 9 de código, 7 figuras
  incrustadas; se comprobó también con `MPLBACKEND=Agg`. El notebook fuente
  conserva todas las salidas vacías y cuentas de ejecución nulas.
- **Controles:** tres comparaciones con los callbacks de widgets (tasa cero,
  acoplamiento cero y valores máximos) y las mismas comparaciones forzando
  la alternativa sin widgets, sin modificar el notebook fuente. Cada variante
  completa las 9 celdas originales y una celda adicional de comprobación.
  Esta evidencia comprueba callbacks; no es una inspección manual del frontend
  de Jupyter o VS Code.
- Con el evento individual, reducir el paso máximo interno a 5 ms produjo
  una diferencia máxima de **1.94 × 10⁻⁸ mV** respecto de la configuración
  predeterminada, por debajo del umbral de 10⁻⁵ mV del notebook.
- Se generaron y revisaron visualmente las cuatro figuras de los ejemplos y
  las del notebook: ejes y unidades legibles, leyendas, supuestos y distinción
  explícita entre función impuesta, voltaje simulado y medición experimental.

| Escenario | Eventos | Mínimo V_O simulado (mV) |
| --- | --- | --- |
| Oscuridad | 0 | -40.000 |
| Fotón individual | 1 | -51.009 |
| Varios fotones definidos | 3 | -55.586 |
| Poisson tenue, semilla 2026 | 3 | -60.424 |

Estos potenciales son resultados de parámetros eléctricos **ilustrativos y no
calibrados**; no son medidas de Baylor. Las figuras y notebooks ejecutados
permanecen en `outputs/`, ignorado por Git. La CI repite los mismos comandos
y publica esos productos como artefactos generados para revisión.

## Preservación y frontera de Git

El directorio inicial contenía solo `Bibliografia/`, con cinco archivos y sin
repositorio Git local ni en directorios superiores. El remoto se comprobó vacío.
Se creó `.gitignore` con `/Bibliografia/` antes de inicializar Git o añadir
archivos. No se clonó, movió ni sobrescribió contenido existente.

Se comparó un inventario local de nombres y SHA-256, guardado fuera del
repositorio: **5/5 archivos idénticos**, sin archivos añadidos o retirados.
La huella se calculó localmente; los documentos privados no se abrieron para
investigación ni se cargaron a servicios externos.

```bash
git check-ignore -v Bibliografia/ Bibliografia/jphysiol00752-0614.pdf
git status --short --ignored
git ls-files -- Bibliografia/
git rev-list --objects --all -- Bibliografia/
git diff main...HEAD --name-only -- Bibliografia/
```

`check-ignore` identifica la regla `/Bibliografia/`; `status` muestra
`!! Bibliografia/`. Los tres últimos comandos deben quedar sin salida:
la bibliografía no pertenece al índice, historial ni cambios del PR.
También se excluyen `.venv/`, cachés y `outputs/`.

`origin` apunta a `https://github.com/EduardoLinceGomez/Neurofisiologia.git`.
`main` contiene la inicialización básica; la implementación se publica en
`feat/rod-three-compartments-minimal`, mediante PR en borrador para revisión
humana. No se autoriza merge ni auto-merge.

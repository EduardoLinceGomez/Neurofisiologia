# Validación del laboratorio pedagógico (Issue #3)

## Entrega actual: estudio guiado

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

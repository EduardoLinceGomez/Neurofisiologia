# Validación de la consolidación de 2026-2

Comprobaciones locales del **6 de noviembre de 2026**, sobre la base
`001eae1ad282cb183d520de0f2a9c10811fbd8f3`. Esta evidencia complementa la
[auditoría](consolidacion_2026-2.md); no sustituye el
[registro de validación del bastón](validacion.md).

## Resultados

| Componente | Resultado | Alcance de la evidencia |
| --- | --- | --- |
| Pruebas vigentes | **115 aprobadas**, 9.17 s | Suite original; sin cambios en código científico ni pruebas |
| Notebook vigente 01 | **9 celdas de código completas**, sin errores | Ejecución con kernel `neurofisiologia` |
| Notebook vigente 02 | **17 celdas de código completas**, sin errores | Ejecución con el mismo kernel |
| Controles vigentes | **4 variantes aprobadas** | 01/02 con callbacks de widgets y alternativa sin widgets |
| Ejemplos vigentes | Terminación satisfactoria | `python -m neurofisiologia.examples`, backend Agg |
| Prueba original de PA | **1 aprobada**, 0.09 s | Reposo y forma/persistencia de caché; no comprueba convergencia general |
| Demo histórica U–D | **2 celdas de código completas**, sin errores | Caché regenerada desde fuentes en `outputs/`; widget construido, sin inspección manual del frontend |
| Proyecto histórico | **104 celdas completas**, con advertencias numéricas | **No se considera numéricamente validado**: overflow/valores inválidos en celdas 150, 161 y 178 (índices desde cero) |
| Laboratorio HH | **No completa ejecución** | `NameError: quasi_ionic_current is not defined`, celda 9, sección 3. Dos celdas de código previas completadas; la tercera se interrumpe y el apéndice no se ejecuta |
| Apuntes tarea 2 | Estructura válida, **0 celdas de código** | Lectura conceptual; no hay un experimento numérico ejecutado |
| Generador HTML HH | Generación satisfactoria | Texto generado igual al HTML previo al normalizar finales de línea; bytes distintos por CRLF/LF. No se probó ejecución de JavaScript ni disponibilidad del CDN en navegador |

Los desbordamientos del proyecto aparecen al calcular familias de trayectorias
con RK4 en varios regímenes; completar las celdas no garantiza que las curvas
sean finitas o válidas. Se conservan las ecuaciones, parámetros y paso originales.
Resolverlo requiere una revisión numérica posterior, separada de la consolidación.
El ejecutor identifica estas advertencias en las salidas y devuelve estado de
revisión pendiente. No es un verificador exhaustivo de resultados numéricos.

La ejecución del proyecto con Agg también avisa que `plt.show()` no dispone de
interfaz interactiva y que hay más de 20 figuras abiertas. Esta corrida comprueba
el cálculo de las celdas; no certifica su presentación visual. La demo PA emitió
`MissingIDFieldWarning`: nbformat asigna identificadores en la copia de ejecución;
el notebook histórico fuente se conserva. No se adaptaron sus metadatos para
ocultar esa limitación de compatibilidad.

El primer intento del proyecto se detuvo por ausencia de `pytz`; se completaron
las dependencias aisladas y se repitió desde cero. El intento final de los cuatro
históricos queda en `outputs/consolidacion_2026-2/resultado.json`: HH incompleto,
proyecto completo con advertencias, U–D sin errores, apuntes sin código.
El código de salida global distinto de cero es **esperado** por esos dos problemas
históricos, y no indica un fallo del bastón.

## Entorno

Python **3.12.14** en macOS; NumPy 2.5.4, SciPy 1.18.1, Matplotlib 3.11.2,
pytest 9.1.1, nbclient 0.11.0, nbformat 5.11.1, ipywidgets 8.1.9.
Se añadieron únicamente las dependencias necesarias para los históricos en
`outputs/consolidacion_2026-2/deps/`: ipympl 0.9.8, SymPy 1.14.0,
pandas 2.3.3, mpmath 1.3.0 y pytz 2026.6. `pip check` con esa carpeta en
`PYTHONPATH` informa **sin incompatibilidades**. El entorno vigente y sus
dependencias declaradas no cambiaron. Las versiones son evidencia local, no
una garantía para otros sistemas o versiones futuras.

## Procedencia, privacidad y preservación

- **124/124 archivos de origen** conservan rutas, tamaños, modos y tiempos de
  modificación frente al inventario inicial. No hay archivos nuevos ni retirados.
  No se ejecutó nada desde el origen. El registro de metadatos permanece local.
- Se compararon hashes iniciales/finales de las fuentes de texto permitidas y
  los **34 pares origen/destino** del manifiesto. Los cuatro notebooks conservan
  exactamente tipo y `source` de cada celda, con salidas vacías y contadores nulos.
  Los otros **30 archivos son idénticos byte a byte**. Las fuentes originales
  completas con sus salidas siguen en 2026-2.
- No se leyó ni calculó hash de los documentos privados, PDF bibliográficos ni
  contenidos de carpetas equivalentes. Su preservación se comprobó únicamente
  por metadatos; no se afirma una comparación de contenido de esos archivos.
- No se encontraron rutas personales ni firmas habituales de credenciales en
  las fuentes seleccionadas. Las diez imágenes manuscritas se revisaron y no
  contienen datos personales visibles ni EXIF. Esto no describe los excluidos.
- Índice e historial local completo revisados mediante árboles Git: **ningún
  archivo de bibliografía privada rastreado**. Se mantiene `/Bibliografia/` y se
  añaden reglas recursivas y variantes con acento. Se comprobaron rutas de
  bibliografía en raíz y anidadas, incluyendo archivos que no son PDF.
- No se añadieron PDF, ZIP, NPZ, HTML generado, bytecode, checkpoints, entornos,
  credenciales ni resultados a Git. Las salidas quedan exclusivamente en
  `outputs/`, ignorado. Los 90 excluidos no forman parte del PR.
- Diferencia vacía frente a `main` para `src/`, `notebooks/`, `tests/`,
  `pyproject.toml`, `AGENTS.md`, decisiones, planes y referencias científicas
  vigentes. No cambian parámetros, estímulos, balances ni integradores del bastón.
- Enlaces relativos de los índices y documentos nuevos, y diez referencias a
  imágenes del proyecto, comprobados contra archivos existentes. No se afirma
  haber probado todos los sitios externos ni cada ancla de notebooks antiguos.
- `git diff --check` se comprueba conservando CRLF del generador histórico mediante
  una regla puntual de `.gitattributes`; no se reformatea el original para
  silenciar avisos de espacio en blanco.

## Repetir y revisar

Desde la raíz del repositorio:

```bash
.venv/bin/python -m pytest -q
MPLBACKEND=Agg .venv/bin/python scripts/execute_notebook.py --kernel neurofisiologia
MPLBACKEND=Agg .venv/bin/python scripts/verify_notebook_controls.py --kernel neurofisiologia
MPLBACKEND=Agg .venv/bin/python -m neurofisiologia.examples
git diff main...HEAD --stat
git diff main...HEAD -- src/ notebooks/ tests/ pyproject.toml AGENTS.md
git check-ignore -v Bibliografia/ materiales/2026-2/Bibliografia/prueba.ipynb outputs/
git ls-files -- Bibliografia/ outputs/
git diff --check main
```

La reproducción histórica y su prueba independiente se detallan en el
[índice de 2026-2](../materiales/2026-2/README.md#reproducir-sin-escribir-sobre-el-archivo).
El manifiesto permite comprobar los destinos sin acceder de nuevo al origen.
Las capturas/validación manual de widgets, revisión científica de los históricos,
procedencia exacta de parámetros y permisos de materiales excluidos quedan
pendientes. No se implementa ON/OFF, no se fusiona el PR ni se activa auto-merge.

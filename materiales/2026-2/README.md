# Archivo de estudio de 2026-2

Estos materiales conservan trabajos del directorio `Posgrado/2026-2/Neurofisiologia`.
Son **históricos**: sus modelos activos, unidades y supuestos no sustituyen al
[bastón pasivo vigente](../../notebooks/02_estudio_guiado_baston.ipynb).
No representan todavía un modelo Cono → Bipolar ON/OFF. Las curvas calculadas son
simulaciones; no deben interpretarse como registros experimentales ni como
calibración de células retinianas.

## Qué estudiar

| Orden sugerido | Material y contenido | Dependencias y advertencias |
| --- | --- | --- |
| 1 | [Tarea 2: energía electroquímica](tarea2/tarea2.ipynb), Nernst, transporte conjunto y ATP | Solo Markdown; lectura sin kernel. La versión de la referencia usada requiere revisión |
| 2 | [Ruta actual 01→02](../../README.md#ruta-de-estudio): signos, unidades, balances, transmisión pasiva | Implementación canónica en `src/neurofisiologia/`, fuera de este archivo |
| 3 | [Proyecto v–w](Proyecto/proyecto1.ipynb): Jacobiana, nulclinas, estabilidad y bifurcaciones | NumPy, SciPy, Matplotlib, SymPy, pandas; 104 celdas de código. Incluye diez hojas manuscritas junto al notebook. Las secciones finales de calcio/ráfagas son antecedentes, no objetivos ON/OFF |
| 4 | [Laboratorio HH](hodgkin_huxley_laboratorio_interactivo.ipynb): umbral, refractariedad, papel de canales | [Dependencias originales](requirements_hh_notebook.txt). Requiere ipympl aunque su introducción lo sugiera opcional. **No ejecuta completo:** falta `quasi_ionic_current` en la sección 3 |
| 5 | [Paquete U–D](PA/proyecto_neurofisiologia_ud_minimo/README.md) y [demo](PA/proyecto_neurofisiologia_ud_minimo/notebooks/01_demo_sistema_ud.ipynb) | Modelo/estímulos/integrador/caché/visualizador separados. La demo necesita construir antes el NPZ. Una prueba aprobada es evidencia limitada, no validación científica |
| Opcional | [Generador HTML HH](generarHTML_HH.py) | Solo biblioteca estándar para generar; navegador con acceso a Plotly 2.35.2 CDN para graficar. Es otra implementación, no probada equivalente al notebook |

El README original de PA conserva caracteres de control en algunas fórmulas.
Para la ecuación legible consulta
[su módulo de modelo](PA/proyecto_neurofisiologia_ud_minimo/src/neurofisiologia_ud/modelos/sistema_ud.py).
Su búsqueda de puntos fijos y el desplazamiento de trazas de la caché tienen
limitaciones registradas en el [informe](../../docs/consolidacion_2026-2.md).
Los históricos se conservan para revisión; sus afirmaciones sobre umbral,
calcio y ráfagas no se certifican por incorporarlos al repositorio.

## Reproducir sin escribir sobre el archivo

Utiliza primero el entorno vigente descrito en el [README principal](../../README.md).
Desde la raíz del repositorio, las dependencias adicionales de esta auditoría
pueden quedar en una carpeta ignorada, sin cambiar ese entorno ni su `pyproject.toml`:

```bash
.venv/bin/python -m pip install --target outputs/consolidacion_2026-2/deps --no-deps -r materiales/2026-2/requirements_auditoria.txt
PYTHONPATH="$PWD/outputs/consolidacion_2026-2/deps" .venv/bin/python -m pip check
PYTHONPATH="$PWD/outputs/consolidacion_2026-2/deps" .venv/bin/python scripts/execute_historical_notebooks.py --kernel neurofisiologia
```

El TXT adicional registra versiones comprobadas de cinco dependencias; no es un
lock completo. `--no-deps` presupone el entorno base ya instalado y se acompaña de
`pip check`. El kernel debe apuntar al mismo Python del entorno vigente. No se
instala el paquete histórico como sustituto del actual: se carga desde la copia
de trabajo por `PYTHONPATH`.

El [ejecutor](../../scripts/execute_historical_notebooks.py) copia únicamente los
archivos enumerados por el manifiesto a `outputs/consolidacion_2026-2/trabajo/`.
Allí genera el HTML y la caché, ejecuta los notebooks sin modificar sus celdas y
guarda resultados/errores en `outputs/consolidacion_2026-2/`. No visita el semestre
original ni la bibliografía. Si falla un notebook, guarda la ejecución parcial,
continúa con los demás y termina con código distinto de cero. El fallo de HH es
conocido; consulta el informe de validación para los demás resultados.

Para ejecutar solo un material, añade `--notebook hh`, `--notebook proyecto`,
`--notebook ud` o `--notebook apuntes`. Este último solo valida estructura: no hay
código que ejecutar. No se considera una reproducción de resultados numéricos.

Para repetir la prueba original de PA:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH="$PWD/materiales/2026-2/PA/proyecto_neurofisiologia_ud_minimo/src" .venv/bin/python -m pytest -q materiales/2026-2/PA/proyecto_neurofisiologia_ud_minimo/tests -o cache_dir=outputs/consolidacion_2026-2/pytest_cache
```

Para explorar widgets manualmente, abre las copias en `outputs/` con el entorno
anterior y sus dependencias adicionales. La prueba automatizada de ejecución
no comprueba la interacción humana ni el renderizado de todos los frontends.

## Procedencia y exclusiones

El [manifiesto](procedencia.json) conserva rutas de origen/destino y SHA-256 de
los 34 archivos incorporados. Se elimina una envoltura de directorio repetida
en PA; el resto conserva nombres y relaciones. Los notebooks mantienen código
y explicaciones celda por celda, sin salidas ni contadores; los demás archivos
son copias byte a byte. Los originales completos permanecen en 2026-2.

No se incorporan bibliografía privada, artículos o PDF de permisos inciertos,
el notebook U–D firmado por un tercero sin licencia establecida, siete figuras
de procedencia incierta, HTML exportados, ZIP, NPZ, checkpoint ni bytecode.
Las atribuciones observadas se conservan y no se asigna una licencia nueva.
Las decisiones y el mapa hacia ON/OFF están en la
[auditoría](../../docs/consolidacion_2026-2.md); la evidencia de ejecución está
en la [validación](../../docs/validacion_consolidacion_2026-2.md).

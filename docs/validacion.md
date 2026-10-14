# Validación de la implementación del Issue #1

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

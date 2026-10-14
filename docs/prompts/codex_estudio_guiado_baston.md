# Encargo a Codex — Laboratorio pedagógico del bastón O–I–T

Implementa el [Issue #3](https://github.com/EduardoLinceGomez/Neurofisiologia/issues/3) del repositorio [EduardoLinceGomez/Neurofisiologia](https://github.com/EduardoLinceGomez/Neurofisiologia). Trabaja en el directorio local existente:

`/Users/lince/Documents/GitHubMac/Posgrado/2027-1/Neurofisiologia`

## Antes de modificar

1. Inspecciona `git status`, ramas, remotos, árbol y `AGENTS.md`. No hagas `reset --hard`, `clean`, force-push ni sobrescribas archivos locales.
2. Lee íntegramente la decisión `docs/decisiones/0001-laboratorio-estudio-baston.md` y la especificación `docs/planes/02-estudio-guiado-baston.md` de la rama remota `docs/estudio-pedagogico-baston`. No asumas que esas rutas ya están en `main`: la documentación está en un PR en borrador y depende de la rama `feat/rod-three-compartments-minimal`.
3. Lee el [PR #2](https://github.com/EduardoLinceGomez/Neurofisiologia/pull/2), su revisión pendiente y el código/notebook existente. No pierdas sus 49 tests ni su comportamiento comprobado.
4. Verifica que `Bibliografia/` sigue intacta, ignorada, sin rastreo ni subidas. **No leas, edites, copies, muevas, borres, publiques ni proceses los documentos de esa carpeta.**

## Flujo de trabajo Git

Si el árbol está limpio y la rama remota existe, crea una rama `feat/rod-guided-study` **a partir de `origin/docs/estudio-pedagogico-baston`**, de manera que incluya la versión del PR #2 y toda la especificación, sin mezclas manuales innecesarias. Si hay modificaciones locales o divergencias, para y explica antes de actuar. Abre al final un **PR en borrador dirigido a `docs/estudio-pedagogico-baston`**, no a `main`, para que la revisión de la implementación no incluya una segunda copia de todos los archivos de la etapa anterior. No merges ni auto-merge.

## Objetivo científico y pedagógico

No expandas el modelo: seguimos con **un bastón pasivo, tres compartimentos O–I–T, acoplamiento axial y fotocorriente impuesta**. Quiero estudiar por qué la luz reduce corriente entrante, cómo cambia el potencial de cada región, qué aportan capacitancias y conductancias, cómo se transporta y atenúa la señal, y qué proviene de mediciones reales.

Conserva la referencia de Baylor, Lamb y Yau (1979), bastones de sapo: célula 1 ≈1.2 pA por respuesta elemental y pico ≈2.2 s. Todo `C`, fuga, reversión y acoplamiento actual es **ilustrativo, no calibrado**. No hacer equivaler un evento fotónico a un spike ni la terminal pasiva a una sinapsis funcional.

## Forma de enseñar

La audiencia maneja EDO, álgebra lineal, programación y métodos numéricos, pero estudia fisiología visual desde sus bases. Quiero rigor matemático **y** motivación biológica.

Organiza cada sección alrededor de una pregunta conceptual: explicación fisiológica simple → significado de variables/unidades → deducción completa → predicción antes de simular → experimento → interpretación → limitación. Usa términos inglés/español en el glosario. Evita metadiscurso, frases vagas, saltos algebraicos y ecuaciones encerradas en cajas.

## Implementación, en este orden

**1. Corregir primero la comparación visual existente.** El baseline actual reutiliza un estímulo al que ya se aplicó la amplitud o la tasa modificada. Construye una referencia genuinamente fija y pruebas que detecten el bug al variar solo amplitud y solo tasa. Para comparar tasas Poisson, muestra cómo cambian los eventos, evita afirmar que una única realización demuestra un efecto causal de la tasa, y define una metodología reproducible.

**2. Simplificar el código para estudio, sin cambiar las EDO.** Añade type hints a funciones públicas, docstrings con ecuaciones, signos, unidades, formas de arrays, entradas/salidas y límites fisiológicos; usa nombres claros y comentarios sobre pasos conceptualmente delicados. Introduce solo las funciones necesarias para descomponer corrientes y medir amplitudes y retardos. No inventes una arquitectura complicada; mantén una sola fuente de verdad de los balances en `src/neurofisiologia/`. Preserva API previa salvo justificación explícita.

**3. Crear `notebooks/02_estudio_guiado_baston.ipynb`.** Debe construir 1 compartimento → 2 → 3, explicar potencial negativo, fuga, corriente axial, corriente fotosensible y reposo oscuro; derivar las tres EDO y opcionalmente la forma matricial. Incluir oscuridad, un evento, varios eventos, superposición, Poisson tenue, comparación de acoplamientos y barridos. Integrar preguntas con predicción, experimento y respuestas razonadas separadas.

**4. Construir visualizaciones pedagógicas precisas** (ver catálogo F1–F8 de la especificación): diagrama vectorial O–I–T con signos; núcleo y eventos; potenciales absolutos y `ΔV`; desglose `I_photo, I_leak, I_axial, I_net`; inspección temporal del circuito; aislado frente a acoplado; sensibilidad paramétrica con mapas en unidades; comparación estocástica. Etiqueta ejes, parámetros fijos, dominios, unidades y suposiciones. Usa Matplotlib, SVG e ipywidgets cuando mejoren la comprensión, con alternativa sin widgets. No imágenes decorativas ni figuras a escala ficticia.

**5. Crear las notas de estudio** `docs/estudio_baston_modelo_minimo.md`, `docs/glosario_neurofisio.md` y `docs/preguntas_de_estudio_baston.md`. Completar referencias con especie, tabla/figura/página, distinguir medida–hipótesis–consecuencia analítica–simulación y registrar la diferencia entre numeración de versiones del trabajo de Herrera-Valdez.

**6. Validar y documentar.** Mantener todos los tests existentes; ampliar pruebas físicas, de métricas, del baseline, del notebook y los callbacks. Ejecutar ambos notebooks completos, CI y ejemplos; revisar todas las figuras visualmente, incluidos desbordamientos y fórmulas. Mantener notebooks fuente sin salidas y productos en `outputs/` ignorado.

## Entrega y criterios de cierre

Publica PR en borrador sin merge ni auto-merge. Reporta: URL, rama y SHA; lista de materiales nuevos; tests y ejecuciones con resultado; ejemplos visuales revisados; explicación de cómo se arregló el baseline; confirmación de `Bibliografia/` fuera de Git; y comandos locales para abrir el estudio desde VS Code.

Si algo exige cambiar el modelo científico, descargar o abrir `Bibliografia/` o introducir dependencias pesadas, **detente y consúltame** antes de hacerlo. La prioridad es comprender y experimentar sobre el modelo mínimo existente, no aumentar su complejidad.

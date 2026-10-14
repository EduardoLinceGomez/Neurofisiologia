# Especificación 02 — Estudio guiado y explorador del bastón mínimo

**Estado:** alcance y criterios de aceptación aprobados para solicitar implementación; sin cambios funcionales efectuados por este documento.  
**Seguimiento:** [Issue #3](https://github.com/EduardoLinceGomez/Neurofisiologia/issues/3).  
**Antecedente:** [PR #2](https://github.com/EduardoLinceGomez/Neurofisiologia/pull/2), bastón O–I–T pasivo.  
**Decisión transversal:** [0001-laboratorio-estudio-baston.md](../decisiones/0001-laboratorio-estudio-baston.md).

## 1. Resultado esperado y audiencia

Entregar un material de **estudio universitario profundo, incremental y reproducible** que combine historia fisiológica, derivación matemática, implementación simple, experimentos controlados, visualizaciones y autoevaluación.

La audiencia maneja EDO, sistemas lineales, métodos numéricos y programación; no suponer conocimientos previos de fisiología. No diluir los pasos matemáticos, pero explicar desde cero potencial de membrana, conductancia, corriente, potencial de reversión, fototransducción y terminología biológica. El texto debe poder leerse como apuntes; el código debe poder estudiarse como formulación del modelo.

La meta no es producir más gráficas por cantidad, sino **responder más preguntas con evidencia**. Antes de cada recurso visual declarar cuál es su propósito.

## 2. Contrato científico inalterable

- Un solo bastón de vertebrado simplificado como tres regiones eléctricas O (outer segment), I (inner segment), T (synaptic terminal); no son tres neuronas. Conducción axial intracelular O↔I↔T.
- Variación impuesta de fotocorriente en O: `I_foto(t) = -Σ A_k h(t-t_k)`, con corriente **entrante positiva**. No son fotones cargados ni una corriente eléctrica que viaja desde el exterior como luz.
- Respuestas efectivas no son potenciales de acción. La terminal no modela todavía la liberación sináptica; su estado es únicamente `V_T(t)`.
- Kernel `h(u)=(u/t_peak)^3 exp(3(1-u/t_peak))` para `u≥0`, cero en otro caso. Es fenomenológico; no infiere cuatro reacciones moleculares.
- Referencia experimental de *bastones de sapo*: Baylor, Lamb y Yau (1979), célula 1, `A=1.2 pA`, `t_peak=2200 ms`. Media intercelular de amplitudes 0.96 pA. El valor 0.20 pA en tabla 1 promedia dispersiones de eventos **dentro** de las células, no es error estándar ni calibración de voltaje.
- Parámetros iniciales **ilustrativos y no calibrados** del PR #2: `C=(20,15,5) pF`; `g_L=(0.05,0.10,0.05) nS`; `E=(-40,-40,-40) mV`; `g_OI=g_IT=0.10 nS`. No reemplazarlos por cifras de otras especies sin trabajo de calibración específico.
- Unidades internas `t: ms, V: mV, C: pF, g: nS, I: pA`. Comprobar `pF·mV/ms=pA` y `nS·mV=pA`.
- Sin cGMP dinámico, sin saturación/adaptación, sin canales activos, sin spikes, sin sinapsis entre células, sin ajuste a mediciones de los tres voltajes. Los experimentos Poisson representan **eventos eléctricos efectivos**, no flujo óptico calibrado.

## 3. Narrativa del notebook nuevo

Crear `notebooks/02_estudio_guiado_baston.ipynb` sin duplicar la implementación en `src/`. Dividir por ideas pequeñas; el principio es **necesidad → concepto → derivación → predicción → simulación → interpretación**. Es preferible más celdas cortas y completas que párrafos densos.

| Paso | Pregunta o logro verificable | Representación / actividad |
| --- | --- | --- |
| 00. Pregunta central | ¿Cómo puede un evento de luz alterar el voltaje de una terminal distante sin generar un spike? | Mapa de qué entra, qué evoluciona y qué sale |
| 01. Bastón real | ¿Qué hacen O, I y T y por qué esta discretización es una aproximación? | Esquema anatómico no a escala; diferencias entre objeto real y nodos matemáticos |
| 02. Mecanismo físico | ¿Por qué la luz **reduce** corriente entrante y causa hiperpolarización? | Secuencia fotón → pigmento → transducina → PDE → cGMP↓ → cierre CNG → corriente oscura↓; distinguir mecanismo real de representación impuesta |
| 03. Vocabulario y convención | ¿Qué quiere decir V=-40 mV, potencial de reversión, corriente entrante, signo de una fuga? | Mini caso con signos, interior vs exterior, dirección de fuerzas |
| 04. Un compartimento | ¿Cómo se deduce `C dV/dt=-g_L(V-E_L)+I(t)` de conservación de carga? | Balance paso a paso; respuesta RC aislada a un pulso ideal didáctico, correctamente rotulado |
| 05. De uno a dos | ¿Qué cambia al conectar O–I? | Corriente axial igual y opuesta; experimento \(g_{OI}=0\) frente a \(g_{OI}>0\) |
| 06. De dos a tres | ¿Dónde intervienen `g_IT`, `C_T`, `g_L,T`? | Tres balances completos y cancelación explícita de corrientes axiales |
| 07. Reposo oscuro | ¿Por qué hay que resolver un equilibrio acoplado cuando `E_j` difiere? | `K V_dark = diag(g_L) E`; comprobación numérica de balance |
| 08. Fotón efectivo | ¿Por qué no modelamos el fotón como carga eléctrica? ¿Qué miden exactamente Baylor y colaboradores? | Fuente y figura 4/tabla 1 con unidades; kernel, escala de amplitud y tiempo al máximo |
| 09. Primera respuesta | ¿Qué ocurre en O, I y T tras un evento y cuánto tarda cada máximo de hiperpolarización? | Evento, `I_photo`, `V`, `ΔV`, marcas temporales y métricas |
| 10. Corrientes ocultas | ¿En qué instantes la fuga o el acoplamiento se oponen o favorecen el cambio local? | Descomposición en corrientes y verificación de balance para un instante seleccionado |
| 11. Acoplamiento | ¿Qué transmite y atenúa la señal? ¿Cuándo no llega a T? | O solo, O–I, O–I–T, misma entrada y mismas constantes donde corresponda |
| 12. Parámetros | ¿Cuál afecta rapidez, amplitud, relajación y transmisión? | Experimentos aislando `C`, `g_L`, `g_OI`, `g_IT`; mapa de sensibilidad |
| 13. Muchos eventos | ¿Qué significa superposición, cuál es la diferencia entre tasa de eventos efectivos y luz incidente? | Suma de kernels; muestra Poisson con semilla; comparación por realizaciones |
| 14. Interpretación avanzada | ¿Qué estructura matemática tiene este sistema lineal? | Opcional: `C \dot u=-K u+e_O I`, modos y variación de constantes; sin ocultar hipótesis |
| 15. Alcance y autoevaluación | ¿Qué podemos concluir y qué requiere otra física o medición? | Preguntas con respuestas separadas, mapa de hipótesis y futuras extensiones |

### Plantilla de cada experimento

1. **Pregunta:** lo que se busca entender, vinculada a un término de la ecuación.
2. **Predicción:** antes de mover controles, escribir signo, tendencia o escala temporal esperada; cuando resulte natural, pedir nivel de confianza.
3. **Experimento controlado:** definir qué cambia y qué permanece fijo, unidades y semilla.
4. **Observación:** curva con métricas numéricas y comparación bien definida.
5. **Interpretación:** explicar mecanismos y límites; distinguir si una conclusión se desprende analíticamente o solo de esta simulación particular.
6. **Comprobación/transferencia:** pregunta nueva y respuesta razonada en una sección inicialmente oculta si el frontend lo permite, con alternativa accesible.

Evitar preguntas sin solución, metáforas sin ecuación que las respalde y vocabulario técnico sin definir.

## 4. Matemática que debe verse íntegra

### Un compartimento

Para `I=0`, derivar equilibrio `V*=E_L` y constante de tiempo `τ=C/g_L`. Para entrada constante `I_0` iniciada en `t_0`, deducir:

\[
V(t)=E_L+\frac{I_0}{g_L}(1-e^{-(t-t_0)/\tau}),\quad t\ge t_0.
\]

Rotularla como **respuesta a entrada de corriente constante**, no como respuesta real de un fotón. Compararla con un evento cuya corriente tiene evolución temporal.

### Sistema O–I–T

Hacer explícitos los tres balances, cada corriente axial con sus dos signos y la cancelación al sumarlos. Incluir:

\[
C=\operatorname{diag}(C_O,C_I,C_T), \qquad
K=\begin{pmatrix}
g_{L,O}+g_{OI}&-g_{OI}&0\\
-g_{OI}&g_{L,I}+g_{OI}+g_{IT}&-g_{IT}\\
0&-g_{IT}&g_{L,T}+g_{IT}
\end{pmatrix}.
\]

Con `V_dark` determinado por `K V_dark=diag(g_L) E` y `u=V-V_dark`:

\[
C\dot u=-K u+e_O I_{\rm foto}(t),\quad e_O=(1,0,0)^\top.
\]

Como ampliación y referencia de validación:

\[
u(t)=e^{-C^{-1}K(t-t_0)}u(t_0)+
\int_{t_0}^{t}e^{-C^{-1}K(t-s)}C^{-1}e_O I_{\rm foto}(s)\,ds .
\]

Indicar qué símbolos son matrices, qué solución es exacta para el modelo y qué curvas se calculan numéricamente con `solve_ivp`. No presentar una curva simulada como medición. Evitar ecuaciones con cajas decorativas.

## 5. Catálogo mínimo de figuras

Cada figura lleva un encabezado de propósito conceptual, unidades, leyendas y supuestos. Priorizar gráficos vectoriales exportables (SVG) y controles en notebook si hay parámetros o tiempo variable. No incluir iconos, ASCII ni imágenes ornamentales.

| ID | Visualización | Pregunta que contesta / elementos obligatorios |
| --- | --- | --- |
| F1 | Diagrama de circuito O–I–T | C, fuga, `E`, acoplamientos y entrada; flechas según convención; esquema no a escala |
| F2 | Kernel y eventos | Instantes de eventos, `h` adimensional, `I_photo` en pA, máximo 2.2 s después del evento si aislado |
| F3 | Voltajes V y desviaciones ΔV | Ejes ms/mV, referencia `V_dark`, mismos colores para O/I/T y marcas del mínimo |
| F4 | Balance descompuesto | `I_photo, I_leak, I_axial, I_net` por nodo en pA, suma numérica consistente |
| F5 | Estado temporal del circuito | Control de tiempo; `V_O,V_I,V_T`, corrientes axiales firmadas y flechas coherentes con las curvas; evitar flechas falsas si la corriente es cero |
| F6 | Aislado / dos / tres compartimentos | Mismo evento y parámetros locales, comparabilidad explícita; métricas de atenuación/retraso |
| F7 | Sensibilidad 2D | `g_OI` vs `g_IT` o `C_O` vs `g_L,O`; colores con métrica y unidad, marca valores por defecto y región evaluada |
| F8 | Variabilidad Poisson | Tren de eventos efectivos y respuesta; distinguir una realización de estadísticos sobre realizaciones y anotar semilla |

Mantener figuras vinculadas en el mismo bloque de explicación cuando permitan comparar simultáneamente. Las leyendas deben indicar **dato experimental** (valores de referencia), **entrada impuesta** y **simulación**; nunca mezclar curvas en el mismo color sin leyenda clara.

### Métricas interpretables

Agregar funciones pequeñas para devolver `min(ΔV_j)` (mV, con signo), `t_min,j` (ms), retardos `t_min,I-t_min,O` y `t_min,T-t_min,O` (ms), y razón de transmisión `|min ΔV_T|/|min ΔV_O|` (adimensional). Tratar respuestas nulas como `None`/`NaN` documentado, nunca inventar un retraso. Distinguir pico de la **corriente** del mínimo de **voltaje**; no son el mismo instante necesariamente.

## 6. Interactividad con significado y comparaciones justas

**Entrada:** amplitud por evento (pA), tiempo al máximo de corriente (ms/s), eventos predefinidos o tasa efectiva (eventos/s), semilla. **Membrana:** capacitancias pF, fugas nS, reversión mV y acoplamientos nS; agrupar por región y empezar con 2–3 controles relevantes, dejando los demás en sección avanzada. **Vistas:** V, ΔV, corrientes, circuito temporal, comparación con referencia y reinicio.

Condiciones:

- En el experimento variando amplitud o acoplamiento, mantener **exactamente iguales los tiempos de eventos** y todos los otros parámetros; indicar cuál fue variado.
- Corregir el fallo existente en `compare_parameters`: actualmente tanto la curva de referencia como la modificada usan un estímulo con `amplitude_scale` y `rate_hz` ya aplicados. Una referencia de amplitud/frecuencia **no es fija** si reutiliza el estímulo modificado. Construir y conservar explícitamente entradas `baseline` y `modified`.
- Si cambia la tasa Poisson, **las entradas ya no son el mismo tren**. Mostrar ambos trenes y corrientes, y no atribuir diferencias individuales exclusivamente a la tasa. Si se usa un acoplamiento por adelgazamiento (thinning) con una realización candidata compartida, explicarlo y probarlo; si no, comparar varias realizaciones o declarar la variación aleatoria residual.
- Los widgets deben funcionar con controles manuales (evitar ejecuciones costosas durante arrastre), conservar una alternativa por funciones de Python y ser operables en JupyterLab/VS Code. Cada control anunciado debe tener efecto comprobable; sin controles decorativos.
- Mantener separados el experimento de **cambiar A por evento** y el de **cambiar frecuencia de eventos**: no enseñar que aumentar brillo significa necesariamente aumentar la amplitud de respuesta de cada fotón.
- No crear un segundo motor científico en JavaScript para una eventual vista HTML. Un HTML autónomo se puede proponer, pero requiere aprobación si añade duplicación, estado difícil de probar o una nueva dependencia grande.

## 7. Refactor de código por legibilidad

Conservar nombres de módulos existentes y su API externa salvo necesidad demostrada. Se permite `src/neurofisiologia/analysis.py` para funciones puras de observación/medidas. Crear `pedagogy.py` únicamente si evita duplicación real y no agrega complejidad.

- Anotar parámetros y tipos de retorno de las funciones públicas (incluida `current_balance`, `simulate` y utilidades de figuras). Especificar para arrays orden `(O,I,T)` y forma `(3,n_t)`, con alias de tipos si aclaran.
- Docstrings en español para explicar **qué se calcula, ecuación, unidades de entrada/salida, signos y limitaciones**. Usar nombres de código claros, incluso en inglés, manteniendo sufijos de unidades `_ms`, `_mv`, `_pa`, `_ns`.
- Presentar una función de desglose de corrientes con nombres explícitos (por ejemplo `leak_current_pa`, `axial_current_oi_pa`, `axial_current_it_pa`, `photocurrent_pa`, `net_current_pa`), asegurando que no existe otra fórmula distinta de la de producción. Para datos por compartimento, aclarar orientación de signos.
- Preferir funciones puras cortas, ejemplos con nombres descriptivos y datos inmutables. Evitar clases auxiliares sin función, abstracciones genéricas, nombres opacos, repetición excesiva de comentarios y trazas que no aclaran la física.
- Conservar rigor de `solve_ivp`, tolerancias y validación; no reemplazar el integrador por Euler en producción. Si se enseña Euler, hacerlo solo como cálculo ilustrativo separado.
- No usar la palabra “congelar” para significar evaluar en un tiempo determinado; describir exactamente qué se mantiene fijo en cada comparación.

## 8. Documentos y organización propuestos

Crear o actualizar:

- `notebooks/02_estudio_guiado_baston.ipynb` — guía incremental y experimentos.
- `docs/estudio_baston_modelo_minimo.md` — notas conceptuales/derivaciones completas.
- `docs/glosario_neurofisio.md` — términos inglés–español, explicación, unidades, advertencia de ambigüedades (potencial de reversión vs reposo, corriente vs voltaje, señal fotónica vs spike).
- `docs/preguntas_de_estudio_baston.md` — predicciones, ejercicios y soluciones al final o plegadas.
- `docs/referencias_y_parametros.md` — fuente/figura/tabla/unidad/especie de cada número; nota sobre variantes de numeración del preprint de Herrera-Valdez.
- `docs/validacion.md` — tests, experimentos, limitaciones, verificación visual.
- `README.md` — ruta de aprendizaje en orden (01 básico, 02 guiado, notas y tests).
- `src/neurofisiologia/`, `tests/`, `scripts/` y flujo de CI solo si son necesarios para apoyar/verificar lo anterior.

No cambiar los cinco archivos de `Bibliografia/`. No copiar PDFs al repositorio. `outputs/` permanece ignorado.

## 9. Pruebas de aceptación

- [ ] Las 49 pruebas existentes siguen pasando; nuevas pruebas para funciones de corrientes, métricas y signos.
- [ ] Se prueba específicamente que cambiar **solo A** y **solo tasa de eventos** cambia el resultado representado respecto de una referencia fija correctamente construida; el control de tasa expone el cambio de entrada y/o su variabilidad.
- [ ] `I_axial(O)+I_axial(I)+I_axial(T)=0` en cada instante (antes de dividir por C); la suma de contribuciones coincide con el balance que integra el solver.
- [ ] Equilibrio oscuro con `E` distintos, fotocorriente causal y negativa, aislamiento al anular acoplamientos, linealidad dentro del rango del modelo.
- [ ] Ejecución automática del notebook 01 y el 02 con outputs locales, fuente sin salidas; validación de widgets y de la alternativa sin widgets.
- [ ] Figuras revisadas visualmente: sin textos sobrepuestos, títulos/símbolos renderizados, ejes/unidades, referencia y simulación inequívocas; diagrama con flechas/signos correctos, vectorial si es viable.
- [ ] `git check-ignore -v Bibliografia/` funciona, `git ls-files -- Bibliografia/` y `git rev-list --objects --all -- Bibliografia/` no listan archivos.
- [ ] CI ejecuta ambas rutas de estudio y los tests, sin subir bibliografía; PR de implementación se publica en borrador, sin merge ni auto-merge.
- [ ] Se entrega un informe con diferencias respecto del primer modelo, pruebas, capturas o artefactos reproducibles y al menos un límite fisiológico identificado correctamente.

## 10. Orden de trabajo para Codex

1. Inspeccionar `AGENTS.md`, el PR #2, el comentario de revisión, este documento y los recursos actuales. Verificar estado local, ruta y protección de bibliografía.
2. Corregir comparaciones de referencia y añadir tests de regresión; comprobar que no cambia la fisiología/EDO del modelo.
3. Añadir el desglose de corrientes y métricas como API simple, tipada y probada.
4. Construir notebook 02 con narrativa y actividades; crear figuras por finalidad, no por cantidad.
5. Escribir notas, glosario, preguntas y tabla de fuentes; actualizar README y CI para ambos notebooks.
6. Auditar científica, matemática y visualmente; ejecutar tests y notebooks; publicar PR en borrador y reportar artefactos.

**No hacer merge.** Detenerse y consultar si aparecen cambios locales inesperados o no se puede conservar `Bibliografia/` sin alteraciones.

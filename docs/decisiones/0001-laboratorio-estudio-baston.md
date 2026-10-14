# Decisión 0001 — Laboratorio de estudio del bastón O–I–T

**Fecha:** 2026-10-14  
**Estado:** decisión documentada; implementación pendiente.  
**Contexto:** [Issue #3](https://github.com/EduardoLinceGomez/Neurofisiologia/issues/3), modelo inicial en [PR #2](https://github.com/EduardoLinceGomez/Neurofisiologia/pull/2).  
**Especificación operativa:** [02-estudio-guiado-baston.md](../planes/02-estudio-guiado-baston.md).

## Problema

El modelo mínimo de un bastón pasivo de tres compartimentos funciona y tiene comprobaciones numéricas, pero tener un simulador no equivale a comprender el fenómeno. El nuevo trabajo debe explicar por qué escogemos las ecuaciones, cómo leer cada corriente, de dónde procede cada número, qué predice la solución y qué no puede concluirse de ella.

Destinatario: persona con formación sólida en EDO, álgebra lineal y métodos numéricos que está aprendiendo fisiología visual. Las explicaciones biológicas comienzan desde fundamentos; las matemáticas no se ocultan ni se sustituyen por analogías imprecisas.

## Decisiones

1. **Mantener el modelo científico mínimo.** Conservar un bastón pasivo, con los compartimentos O (outer segment), I (inner segment) y T (synaptic terminal). Luz → variación negativa de corriente impuesta en O. O↔I y I↔T son uniones axiales *dentro de la misma célula*, no sinapsis. La terminal aún no libera glutamato en el modelo. Los eventos fotónicos no son spikes.
2. **Enseñar progresivamente.** Introducir primero un compartimento, luego la pareja O–I y finalmente O–I–T. Antes de cada simulación: pregunta física → predicción justificada → experimento → interpretación en lenguaje natural → contraste matemático.
3. **Mantener capas separadas.** `src/neurofisiologia/` es la fuente única del modelo y del análisis; los notebooks enseñan y llaman a esas funciones, sin copiar EDO ni fórmulas de producción. Una refactorización se aprueba por mejorar legibilidad y preservar comportamiento; no crear capas abstractas innecesarias.
4. **Hacer visible la conservación de carga.** Descomponer fuga, fotocorriente, corriente axial y corriente neta por compartimento; conectar cada curva con un término de la EDO; incluir un diagrama vectorial y, cuando aporte comprensión, un control de tiempo para inspeccionar el estado.
5. **Visualización matemática rigurosa.** Cada figura debe responder una pregunta concreta y etiquetar variables, dominios, unidades, condiciones, signos y parámetros fijos/variables. Identificar lo exacto, numérico y esquemático; figuras esquemáticas nunca se presentan a escala. Preferir SVG vectorial y figuras interactivas cuando existe variación relevante; no usar ASCII decorativo, imágenes sin función ni ecuaciones encerradas en recuadros.
6. **Trazabilidad científica obligatoria.** Separar explícitamente (a) medición experimental, (b) elección de modelo, (c) consecuencia matemática y (d) resultado numérico. Baylor, Lamb y Yau (1979) mide corriente de *segmento externo de bastones de sapo*; el modelo no ajusta voltajes reales. Los `C_j`, `g_{L,j}`, `E_j` y acoplamientos actuales son ilustrativos, no estimaciones de laboratorio.
7. **Interactividad que razona.** Los controles deben corresponder a magnitudes con unidad y mecanismo definido. Evitar sliders inertes o comparaciones engañosas. Una referencia de comparación debe ser auténticamente fija y rotulada; la variabilidad de trenes Poisson debe separarse del efecto paramétrico.
8. **Resultados reproducibles y estudiables.** Mantener notebooks fuente limpios, pruebas automáticas, ejecuciones verificadas y salidas en `outputs/` (ignorado). Incluir ejercicios con respuestas ocultables o en sección separada, para ensayar explicaciones sin ver inmediatamente la solución.
9. **Privacidad y gobierno de versiones.** `Bibliografia/` permanece íntegra, local y excluida de Git. Prohibidos borrados, movimientos, copias o subidas de su contenido. Trabajar por ramas, PR en borrador y revisión; no fusionar ni activar auto-merge sin autorización.

## Matemática que debe entenderse, no solo ejecutarse

Partir de `C dV/dt = -g_L(V-E_L) + I(t)` y construir los tres balances:

\[
\begin{aligned}
C_O \dot V_O &=-g_{L,O}(V_O-E_O)+g_{OI}(V_I-V_O)+I_{\mathrm{foto}}(t),\\
C_I \dot V_I &=-g_{L,I}(V_I-E_I)+g_{OI}(V_O-V_I)+g_{IT}(V_T-V_I),\\
C_T \dot V_T &=-g_{L,T}(V_T-E_T)+g_{IT}(V_I-V_T).
\end{aligned}
\]

Distinguir corriente entrante positiva del cambio negativo inducido por luz. El equilibrio oscuro `V_dark` se calcula a partir del sistema acoplado, no se presupone igual a cada `E_j` si difieren. Para estudiar desviaciones `u=V-V_dark`, construir `C du/dt=-K u + e_O I_foto(t)`, con `C` diagonal y `K` simétrica. La solución por variación de constantes puede presentarse como ampliación matemática opcional y como prueba independiente, no como requisito fisiológico previo.

## Evidencia y versiones de fuentes

- **Baylor, Lamb y Yau (1979), J. Physiol. 288:613–634:** tabla 1 (p. 621): célula 1, amplitud de referencia ≈1.2 pA; figura 4 (p. 619): respuesta cuya escala al máximo es ≈2.2 s. El promedio entre ocho células es 0.96 pA (tabla 1). Es registro de corriente de bastón de sapo: ninguna de estas fuentes proporciona `C_O,C_I,C_T` o tres voltajes compartimentales calibrados.
- **Herrera-Valdez (2026):** especificar siempre edición usada. El PDF fechado 1 de septiembre de 2026, sección 3.6, contiene el balance multicompartmental en ecuación (36); una versión anterior pública puede tener numeración diferente (citada como ecuación 38). No mezclar localizadores como si correspondieran al mismo documento.
- **Hodgkin y Huxley (1952):** principio de balance capacitivo y corrientes iónicas; no importar sin justificación parámetros del axón de calamar al bastón.

## Alternativas pospuestas

No iniciar todavía modelos de cono o amacrina, conductancias fotosensibles dependientes de cGMP, bioquímica explícita, sinapsis intercelulares, canales de Ca²⁺ o Na⁺ activos, generación de spikes, identificación de parámetros desde datos ni una interfaz web separada compleja.

**Criterio de éxito:** una persona puede reconstruir el balance, predecir el signo y orden temporal de las respuestas, explicar el papel de cada parámetro y distinguir los límites del modelo sin depender de respuestas ocultas ni de leer primero el código.

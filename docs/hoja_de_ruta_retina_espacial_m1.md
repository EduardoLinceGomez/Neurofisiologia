# Panorama general del proyecto: retina espacial, centro–periferia y movimiento

**Fecha de decisión:** 13 de noviembre de 2026.  
**Estado:** hoja de ruta científica y técnica aprobada como **dirección de trabajo**, sin implementación M1 ni calibración biológica todavía.  
**Seguimiento:** [Issue #10](https://github.com/EduardoLinceGomez/Neurofisiologia/issues/10) y [PR #11](https://github.com/EduardoLinceGomez/Neurofisiologia/pull/11).  
**Especificación matemática detallada:** [M1 centro–periferia y dirección](especificacion_m1_centro_periferia_direccion.md).

## 1. Pregunta general

**¿Cómo pueden respuestas graduadas locales ON/OFF transformarse, mediante procesamiento espacial y temporal, en detección de contrastes, campos receptivos centro–periferia y preferencia por direcciones de movimiento?**

Se estudiarán por separado tres fenómenos, que no son intercambiables:

1. **Signo ON/OFF**: una disminución del glutamato del cono produce aumento de conductancia ON y disminución OFF. El modelo M0 con un cono y dos bipolares ya permite estudiar esto; **no hace falta una red** para invertir la señal.
2. **Centro–periferia**: responder de manera opuesta a un incremento de luz en una zona central o en sus alrededores. Las células horizontales intervienen en la retina real; un filtro de contraste en M1-A/C será **fenomenológico, no una sinapsis horizontal modelada**.
3. **Selectividad direccional**: distinguir movimientos opuestos con idénticos contraste, anchura, trayectoria y rapidez absoluta. Necesita asimetría de integración espaciotemporal o conectividad; una población ON/OFF y una periferia antagonista **no generan automáticamente dirección**.

**Hipótesis orientadoras, no resultados garantizados:** (H1) un filtro espacial antagonista genera contraste centro–periferia en su lectura sin alterar M0; (H2) filtros temporales + conectividad orientada + umbral local pueden distinguir sentidos de movimiento; (H3) la selectividad puede depender de la geometría, las fronteras y la heterogeneidad. La investigación busca someterlas a controles, no imponerlas al simulador.

## 2. Objetivos específicos y preguntas operativas

| Objetivo | Pregunta | Herramienta matemática | Indicador / control |
|---|---|---|---|
| O1. Reproducir ON/OFF local | ¿Cómo producen las conductancias efectos postsinápticos opuestos? | EDO RC + r(V) + g_ON/OFF | signos, reposo y corrientes; M0 independiente |
| O2. Obtener centro–periferia | ¿Qué responden el centro, un anillo y una iluminación uniforme? | filtros espaciales discretos y kernels radiales | respuesta central vs entorno; prueba uniforme |
| O3. Obtener selectividad direccional | ¿Qué retrasos/conexiones y umbrales distinguen ±v? | memoria temporal, no linealidad local y detectores espejo | Q_pref, Q_null, DSI, velocidad óptima; control sin filtro |
| O4. Evaluar el papel de la geometría | ¿Es equivalente una retícula triangular de centros hexagonales a una cuadrada? | geometría discreta, distancias euclidianas, grafos, simetrías | rotaciones 60°, sesgos angulares y comparación justa |
| O5. Medir robustez | ¿Qué sucede con posiciones perturbadas o conexiones eliminadas? | grafos perturbados y barridos de parámetros | distribución de DSI y Q, incertidumbre de simulación |
| O6. Contrastar con fisiología | ¿Qué predicciones del modelo son observables y cuáles son hipótesis? | interpretación de potencial, conductancia, calcio y conectividad | mapa de supuestos, datos requeridos y límites |

## 3. Etapas mínimas, con criterio de terminación

### Etapa 0: M0 actual (referencia científica)
- **Geometría:** un cono que alimenta una bipolar ON y otra OFF, tres células de un compartimento.
- **Herramienta:** tres EDO de voltaje, liberación sigmoidal algebraica y conductancias sinápticas catiónicas.
- **Producto:** contrastes, corrientes, equilibrio y validación de signos.
- **Estado:** ya implementado en [PR #8](https://github.com/EduardoLinceGomez/Neurofisiologia/pull/8), todavía independiente del trabajo de este documento.

### Etapa 1: M1-A — centro y dos vecinos
- **Geometría:** tres posiciones **1D** izquierda–centro–derecha. Cada posición contiene una unidad M0 completa (nueve EDO de membrana).
- **Lectura:** \`S_C=u_C-\kappa(u_L+u_R)/2\`.
- **Experimentos:** iluminar solo el centro, solo los vecinos, las tres posiciones uniformemente y un patrón móvil.
- **Criterio:** inversión de signo *de la lectura espacial*, cancelación para un cambio uniforme con κ=1 y ausencia de cambios artificiales en las ecuaciones M0. **No confundir S_C con el voltaje de una bipolar biológicamente acoplada**.

### Etapa 2: M1-B — detector mínimo de movimiento
- **Geometría:** cinco posiciones 1D, quince EDO M0 y cinco EDO de filtros temporales para **una vía seleccionada** (20 EDO).
- **Lectura:** actividad \`a_i=[u_i/A_ref]_+\`, filtro \`τ_d y_i'=a_i-y_i\`, coincidencia local \`c_i^→=[y_i+a_{i+1}-θ]_+\`, detector espejo \`c_i^←=[y_{i+1}+a_i-θ]_+\`. Sumar **después** de aplicar el umbral local.
- **Experimentos:** barra brillante ON / barra oscura OFF, ±velocidad, tiempo de integración, umbral, ventana de observación y simetría por reflexión.
- **Criterio:** preferencia que depende realmente del orden temporal de activación y desaparece cuando no hay asimetría temporal. No implementar spikes solo por usar un umbral fenomenológico.

### Etapa 3: M1-C — malla 2D hexagonal como geometría principal
- **Geometría elegida:** **red triangular de centros**, seis vecinos cercanos, regiones de Voronoi hexagonales; **no** grafo de panal con tres vecinos por vértice.
- **Coordenadas:** \`(x,y)=a(q+r/2, √3 r/2)\`. Región hexagonal de \`R\` anillos con \`N=1+3R(R+1)\`.
- **Escalas:** comenzar con \`R=3 → N=37\` (111 EDO M0 + 37 filtros = 148 EDO). Comparar \`R=4 → N=61\` (244 EDO). \`a\` será primero una distancia normalizada.
- **Estímulos:** disco central, anillo, iluminación uniforme, bordes móviles y manchas circulares en trayectorias de diferentes ángulos.
- **Campos:** kernels de centro y periferia basados en **distancias euclidianas** y normalizados por nodo; para un cambio uniforme, \`κ=1\` da \`S=0\`.
- **Criterio:** mapas interpretables de actividad; invariancia frente a rotaciones de 60° de una región ideal; sesgos angulares cuantificados; sin respuesta direccional producida exclusivamente por fronteras.

### Etapa 4: redes perturbadas y sensibilidad
- **Experimentos:** desplazar ligeramente nodos, cambiar distancias y pesos, eliminar enlaces de lectura, variar τ y θ, comparar regiones R=3 y R=4.
- **Control:** usar semillas aleatorias registradas, repetir muestras, mostrar **magnitudes** de respuesta además de DSI.
- **Criterio:** identificar qué propiedades son robustas y cuáles dependen de un empaquetamiento o un parámetro elegido.

### Etapa posterior (NO forma parte de M1)
Si las preguntas o los datos lo justifican, estudiar una célula horizontal explícita para centro–periferia, o un modelo compartimental de dendritas *starburst*, GABA/ACh y ganglionar para dirección. Estos mecanismos **no se simulan** con los filtros algebraicos M1.

## 4. Matemática y software: contratos

| Capa | Formalismo | Herramientas | Separación obligatoria |
|---|---|---|---|
| Fisiología local | tres EDO M0 por posición | Python, NumPy, SciPy \`solve_ivp\` | reutilizar \`retina_on_off.py\`, sin copiar las RHS |
| Geometría | coordenadas axiales, distancias, vecinos, Voronoi opcional | NumPy y \`scipy.spatial\` | posición ≠ neurona individual ≠ conexión sináptica |
| Conectividad | pesos y operadores de lectura sobre un grafo | NumPy y \`scipy.sparse\` | una arista computacional no prueba sinapsis anatómica |
| Centro–periferia | diferencia de kernels normalizados | matrices/operadores espaciales | filtrado fenomenológico, no horizontal explícita |
| Detector | EDO de filtro, integración local y umbral | SciPy + álgebra vectorizada | el signo direccional no se impone en el código |
| Análisis | Q, DSI, máximos, convergencia, simetrías | NumPy, SciPy, pytest | no interpretar un DSI alto si Q es casi cero |
| Visualización | mapas temporales, disco/anillo y curvas sincronizadas | Matplotlib, ipywidgets opcional | notebooks consumen módulos, no redefinen modelo |
| Reproducción | versionado, pruebas, notebook ejecutado | GitHub, PR, GitHub Actions, nbclient | \`Bibliografia/\` privada intacta |

**API objetivo:**
\`\`\`python
resultado = simulate_m1(
    tiempos_ms, geometria, estimulo,
    parametros_m0, parametros_espaciales, parametros_detector
)
\`\`\`

**Datos devueltos:** \`L(x,t)\`, voltajes de cono/ON/OFF, liberación, conductancias, lectura centro–periferia, señales filtradas, coincidencia local, respuestas direccionales y métricas. Mantener una **referencia canónica fija** en exploraciones de parámetros.

**Estructura futura, aún no implementada:** \`src/neurofisiologia/retina_movimiento/{geometria,estimulos,poblacion,campos_receptivos,detectores,simulacion,analisis,figuras}.py\`, \`notebooks/04_retina_espacial_y_direccion.ipynb\`, \`tests/test_retina_espacial_m1.py\`.

La implementación científica debe partir de PR #8 o de un \`main\` que ya lo incorpore; nunca recrear/copiar M0 ni mezclar los PR #6 (histórico) y #9 (enlaces públicos) por conveniencia. Usar PR en borrador, sin merge o auto-merge sin orden posterior.

## 5. Criterios mínimos de verificación científica

1. **M0:** signos y equilibrios estables, sin alteraciones.
2. **Geometría:** cada posición está correctamente proyectada; la malla regular tiene seis vecinos interiores y simetría hexagonal. Los bordes se verifican explícitamente.
3. **Centro–periferia:** el filtro de contraste uniformemente iluminado cancela con κ=1, pero no atribuir la cancelación al voltaje M0 de cada bipolar.
4. **Dirección:** el experimento reflejado cambia de preferencia; con \`y_i=a_i\`, dos detectores espejo son iguales. Registrar efectos de la ventana temporal.
5. **Control de discretización:** refinar paso temporal y, cuando corresponda, tamaño espacial no debe cambiar arbitrariamente resultados clave.
6. **Red:** perturbaciones reproducibles y estadísticas entre múltiples realizaciones; igualdad de contraste, duración y área al comparar geometrías.
7. **DSI:** definido solo si el denominador es positivo; reportar \`Q_pref\`, \`Q_null\` y escala de respuesta siempre.
8. **Pedagogía:** cada gráfico tendrá hipótesis, variables/unidades, pregunta, predicción e interpretación. Validar notebook con y sin widgets.

## 6. Bibliografía de orientación

- [Webvision, *How the Retina Works*](https://www.ncbi.nlm.nih.gov/books/NBK610611/): campos centro–periferia e interacción horizontal.
- [Diamond (2017), *Inhibitory Interneurons in the Retina*](https://doi.org/10.1146/annurev-vision-102016-061345): horizontal y amacrina como circuitos laterales distintos.
- [Sawides et al. (2016), *Cone photoreceptor mosaic*](https://pubmed.ncbi.nlm.nih.gov/27353225/): tendencia triangular/hexagonal con irregularidad y anisotropía local.
- [Pitcher et al. (2026), *Retinal waves shape starburst amacrine cell dendrite development*](https://pmc.ncbi.nlm.nih.gov/articles/PMC13374506/): ejemplo actual de procesamiento dendrítico direccional, que motiva una futura comparación fisiológica, no los parámetros M1.

**Conclusión operativa:** estudiar primero M0 → M1-A (tres posiciones) → M1-B (cinco posiciones) → M1-C (malla hexagonal 37/61 posiciones) → robustez. Esta ruta prioriza la **pregunta científica** sobre la complejidad del software. No se autoriza confundir una relación de lectura fenomenológica con un mecanismo fisiológico detallado.

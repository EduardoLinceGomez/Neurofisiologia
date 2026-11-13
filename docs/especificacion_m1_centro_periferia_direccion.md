# Diseño científico M1: de ON/OFF local a campos receptivos y detección de dirección

**Estado:** propuesta v0.1, 9 de noviembre de 2026. **No implementada; pendiente de discusión y aprobación científica del autor.**

**Seguimiento:** [Issue #10](https://github.com/EduardoLinceGomez/Neurofisiologia/issues/10).  
**Base fisiológica computacional:** [M0 Cono → Bipolar ON/OFF, PR #8](https://github.com/EduardoLinceGomez/Neurofisiologia/pull/8) (en borrador cuando se creó esta especificación).  
**Otro trabajo independiente:** PR #6, consolidación histórica. No modificar el modelo del bastón ni el material histórico.

## 1. Preguntas y distinciones esenciales

La pregunta anterior era: ¿cómo la misma disminución de glutamato despolariza a una bipolar ON e hiperpolariza a una OFF? **M0 la responde localmente con una sola sinapsis presináptica y dos postsinápticas efectivas.** No necesitamos una red para demostrar ese cambio de signo.

La nueva pregunta combina dos problemas que conviene separar antes de conectar:

1. **Campo receptivo centro–periferia (center–surround):** ¿cómo cambia una respuesta al iluminar el centro de una región, un anillo alrededor o todo el campo? En retina real, la inhibición/retroalimentación lateral de células horizontales contribuye a la periferia antagonista de las bipolares. El circuito M0 aislado **no** representa esta interacción.
2. **Selectividad direccional (direction selectivity):** ¿cómo distingue una red un estímulo que avanza hacia la derecha del mismo estímulo avanzando hacia la izquierda? Se requiere una operación espaciotemporal con orden/retrasos o asimetría de conexiones; ON/OFF y centro–periferia por sí solos no bastan.

En esta especificación, «bola» se interpreta como **mancha o disco luminoso proyectado sobre la retina**, no como esfera física 3D. ON/OFF se refiere al signo de la respuesta local del centro; ON-centro/OFF-periferia describe una arquitectura espacial; detector de dirección es un procesamiento adicional.

Una **posición espacial** no equivale a una sola neurona: cada punto M0 contiene un cono, una bipolar ON y una OFF (tres variables de membrana). Una red de cinco posiciones tiene quince variables de membrana antes de los filtros detectores. La convergencia real depende del tipo de bipolar y localización retinal; algunas vías foveales pueden transmitir la señal de un único cono, mientras otras integran varios.

## 2. Ruta experimental y niveles de abstracción

| Fase | Geometría | Qué se modela | Qué **no** se afirma |
|---|---|---|---|
| **M0** (existente, PR #8) | Un punto | Fotocorriente efectiva, r(V_C), dos conductancias ON/OFF, 3 EDO | Campo receptivo espacial, horizontal, amacrina o spikes |
| **M1-A** (primer experimento) | **1D, 3 posiciones** | Centro frente a vecinos y signo de un filtro lateral | Un anillo/círculo 2D o sinapsis horizontal real |
| **M1-B** (detector inicial) | **1D, 5 posiciones** | Barra móvil, respuestas ON/OFF locales, filtros temporales, coincidencia y umbral | Célula ganglionar fisiológica calibrada o generación de spikes |
| **M1-C** (extensión espacial) | **2D, 7×7**; explorar 9×9 | Mancha, anillo, campo radial centro–periferia y movimiento planar | Células horizontales o starburst explícitas |
| **M2 futuro** | 1D/2D según datos | Horizontal real, dendritas starburst, inhibición GABA/ACh y ganglionares si se justifica | No añadirlas en M1 sin hipótesis y datos verificables |

**Decisión propuesta:** M1-A es la lección analítica; M1-B es el primer laboratorio de selectividad direccional; M1-C es la evolución más natural para estudiar manchas circulares. La representación espacial no requiere docenas de neuronas para ilustrar la idea: sí requiere más puntos para resolver radios, periferia, bordes y direcciones de un estímulo realista.

## 3. Núcleo: repetir M0 sin modificarlo

En posiciones `x_i=i Δx`, con fondo `L_0>0`, cada punto recibe `L_i(t)≥0`. Reutilizamos las ecuaciones de M0, sin copiar su implementación en un nuevo notebook:

```math
C_C \dot V_{C,i}=-g_{L,C}(V_{C,i}-E_C)-k_L[L_i(t)-L_0],\quad
r_i=\left(1+e^{-(V_{C,i}-V_{1/2})/s}\right)^{-1},
```

```math
g_{ON,i}=\bar g_{ON}(1-r_i),\quad g_{OFF,i}=\bar g_{OFF}r_i,
```

```math
C_b\dot V_{b,i}=-g_{L,b}(V_{b,i}-E_{L,b})
 +g_{b,i}(E_{syn,b}-V_{b,i}),\quad b\in\{ON,OFF\}.
```

**Convención:** corriente entrante positiva, unidades `ms, mV, pF, nS, pA`. `L` y `r` permanecen adimensionales y no calibradas. Los voltajes y el reposo deben calcularse por unidad, con sinapsis basal abierta. `V_{b,i}^{*}` es el equilibrio para `L_i=L_0`. Los cálculos de integración no deben interpretar la red como cable axial entre puntos: cada M0 es independiente y la interacción aparece inicialmente **en una lectura espacial efectiva**.

### Estímulo 1D para movimiento

```math
L_i(t)=L_0+A B(x_i-x_c(t)),\quad x_c(t)=x_{start}+vt,\quad
B(z)=\begin{cases}
\tfrac12[1+\cos(\pi z/w)],&|z|\le w,\\
0,&|z|>w.
\end{cases}
```

`A>0`: mancha/barra brillante; `A<0`: mancha oscura, siempre `L_i(t)≥0`. `v` es **velocidad con signo**, en `espaciado/ms`; `Δx=1` espacio normalizado y `|v|=0.025` implica 40 ms entre posiciones vecinas. Elegir inicio y fin fuera del dominio para comparar direcciones con igual trayectoria, duración de exposición, contraste y `|v|`. No afirmar ancho físico ni intensidad en fotones reales.

## 4. M1-A: tres vecinos y antagonismo centro–periferia

Sean `u_i^b(t)=V_{b,i}(t)-V_{b,i}^*` las desviaciones para una vía `b∈{ON,OFF}`. Para las posiciones izquierda `L`, centro `C` y derecha `R`:

```math
S_C^b(t)=u_C^b(t)-\frac{\kappa}{2}\bigl(u_L^b(t)+u_R^b(t)\bigr),
\qquad 0\le\kappa\le1.
```

Interpretación **exclusivamente fenomenológica**: salida de contraste central contra vecinos. No equivale a corrientes sinápticas laterales en la bipolar de M0 ni incorpora aún una célula horizontal. Si `κ=0`, no hay entorno antagonista; si `κ=1` y `u_L=u_C=u_R`, la lectura `S_C=0`. Para una mancha brillante centrada y vía ON, `S_C^{ON}>0` si prevalece el centro; iluminación solo en ambos vecinos puede volver `S_C^{ON}<0` aunque el potencial de la bipolar central original no cambie. La condición para una vía OFF-centro puede probarse con una mancha oscura.

**Tres posiciones bastan para enseñar este contraste y dos orientaciones de movimiento**, pero son pocos puntos para medir anchura/anillo circular, heterogeneidad o robustez. No extrapolar `S_C` como si fuese el voltaje real de una bipolar con circuito horizontal resuelto.

**Experimentos mínimos:** iluminamos (i) solo centro, (ii) solo vecinos, (iii) las tres posiciones por igual y (iv) un patrón izquierda→centro→derecha. Mostrar `L_i`, `V_{ON,i}`, `V_{OFF,i}`, `S_C^{ON/OFF}`, antes y después de activar `κ`.

## 5. M1-B: cinco posiciones y detección de movimiento

Primero activar una sola vía `b`: ON para una mancha brillante sobre el fondo, OFF para una oscura. Definir una respuesta espacial opcional `S_i^b` que sea igual a `u_i^b` si `κ=0` y, si `κ>0`, reste un promedio ponderado de las posiciones vecinas. Exigir pesos no negativos, suma uno, tratamiento simétrico de bordes explícito y control de iluminación uniforme. La lectura del detector es:

```math
a_i(t)=[S_i^b(t)/A_{ref}]_+,\qquad [z]_+=\max(0,z),
```

con `A_ref>0` constante para todas las comparaciones; elegirla de una prueba estacionaria **canónica**, no recalcularla para cada contraste o dirección.

Filtro temporal de primera orden:

```math
\tau_d\dot y_i=a_i-y_i,\qquad y_i(0)=0,\quad\tau_d>0.
```

Es **memoria distribuida exponencial**, no una demora física fija. Para el control sin filtro, definir explícitamente `y_i=a_i` (sin dividir por `τ_d=0` en la EDO).

Coincidencia de parejas adyacentes, con detectores espejo:

```math
c_i^{\rightarrow}=[y_i+a_{i+1}-\theta]_+,\qquad
c_i^{\leftarrow}=[y_{i+1}+a_i-\theta]_+,
\quad\theta\ge0.
```

Suma **después** de aplicar el umbral local:

```math
R_{\rightarrow}(t)=\sum_{i=0}^{N-2}c_i^{\rightarrow}(t),\qquad
R_{\leftarrow}(t)=\sum_{i=0}^{N-2}c_i^{\leftarrow}(t).
```

**Por qué la no linealidad local es indispensable:** si se quitara `[\cdot]_+` y se restaran las dos sumas lineales, todos los términos interiores se cancelarían:

```math
\sum_{i=0}^{N-2}(y_i+a_{i+1})
-\sum_{i=0}^{N-2}(y_{i+1}+a_i)
= y_0-y_{N-1}+a_{N-1}-a_0.
```

La diferencia lineal resultaría artificialmente dominada por los **bordes** del dominio y no mediría coincidencias locales. El umbral aplicado a cada par cambia esta propiedad.

**Número de EDO:** `3N` variables de voltaje M0 y `N` de filtro para **una vía** ON u OFF seleccionada, total `4N` (`20` para cinco posiciones). Si se filtran simultáneamente ON y OFF con estados separados, serán `5N` EDO; no confundir con la primera versión. La coincidencia es algebraica y no una EDO ganglionar ni spikes.

**Predicciones/controles:** la respuesta debe cambiar al invertir `v` sin alterar `|v|`; intercambiar los canales espejo bajo reflexión espacial; con `y_i=a_i`, los dos detectores son algebraicamente iguales; con `θ` muy alto, ambos quedan silenciosos. No tomar una diferencia de amplitudes causada por fronteras o tiempos de observación como selectividad direccional neuronal.

## 6. M1-C: extensión natural a 2D

Pasar a posiciones `(x_i,y_j)` en una retícula `N_x×N_y`; comenzar por `7×7`, comparar `9×9`. Para una mancha brillante/oscura circular, usar inicialmente el estímulo radial suave:

```math
L_{ij}(t)=L_0+A B(\rho_{ij}(t)),\quad
\rho_{ij}(t)=\sqrt{(x_i-x_c(t))^2+(y_j-y_c(t))^2},
```

```math
B(\rho)=\begin{cases}
\tfrac12(1+\cos(\pi\rho/R)),&0\le\rho\le R,\\
0,&\rho>R.
\end{cases}
```

El centro puede permanecer fijo o recorrer una trayectoria en `(x,y)`. Para aislar el entorno, definir un **anillo** espacial y comparar estímulos centro, periferia, disco completo y fondo uniforme, siempre dentro del campo.

Lectura espacial centro–periferia como diferencia de kernels radiales normalizados:

```math
S_{ij}^b=(K_c*u^b)_{ij}-\kappa(K_s*u^b)_{ij},\quad
\sum K_c=\sum K_s=1,\qquad\sigma_s>\sigma_c.
```

En esta fase son kernels **fenomenológicos**. Para `κ=1`, un cambio uniforme debe cancelar en la lectura cuando el tratamiento de fronteras preserva constantes (por ejemplo reflexión/simetría y normalización correcta). Probar explícitamente el comportamiento en los bordes y no introducir anisotropía artificial al girar la mancha. Para enseñar 2D de modo que se distingan centro y periferia, `3×3` es muy grueso; `7×7` y `9×9` son opciones de laboratorio, no estimaciones de densidad celular real.

En una sola vía, `N=49` implica `147` EDO M0 y `49` filtros (`196` EDO); `N=81` implica `243+81=324` EDO. No introduce dificultad conceptual nueva ni requiere un simulador de neuronas biológicamente detallado. Para dirección planar, comparar primero `±x`, `±y` y luego diagonales, aplicando los mismos mecanismos y parámetros después de rotar/reflejar el estímulo y la disposición del detector.

**Observación fisiológica:** el antagonismo centro–periferia en retina está relacionado con células horizontales y vías laterales. **Esta lectura filtrada no sustituye una implementación mecanística** de la sinapsis horizontal–cono/bipolar, que se reserva para M2.

### Alternativa M1-C-H: malla hexagonal de conos (en evaluación, 13 de noviembre de 2026)

**Propuesta geométrica:** evaluar como primera opción de M1-C una **red triangular de centros celulares con seis vecinos inmediatos**, cuyo diagrama de Voronoi produce celdas aproximadamente hexagonales. **No confundir con el grafo de panal (honeycomb) de vértices de hexágonos, que tiene tres vecinos por vértice.** Una posición computacional sigue representando una unidad M0 (cono, ON, OFF), no un soma con seis sinapsis biológicas ya demostradas.

Para índices axiales enteros `(q,r)` y separación `a>0`, colocar cada posición en coordenadas cartesianas:

```math
(x_{q,r},y_{q,r})=a\left(q+\frac{r}{2},\frac{\sqrt3}{2}r\right).
```

Los vecinos de primer orden tienen desplazamientos `(±1,0)`, `(0,±1)`, `(1,-1)` y `(-1,1)`. La distancia al centro de la retícula, expresada en número de anillos, es `d_{hex}(q,r)=max(|q|,|r|,|q+r|)`. Para una región hexagonal de radio entero `R`:

```math
\mathcal H_R=\{(q,r)\in\mathbb Z^2:\max(|q|,|r|,|q+r|)\le R\},
\qquad N(R)=1+3R(R+1).
```

- `R=3`: **37 posiciones**, **111** EDO de voltaje M0 y **37** filtros = **148 EDO** si se filtra una sola vía.
- `R=4`: **61 posiciones**, **183** EDO M0 y **61** filtros = **244 EDO**.
- `R=5`: **91 posiciones**, **273** EDO M0 y **91** filtros = **364 EDO**.
- Alternativa original `7×7` cuadrada: 49 posiciones, 196 EDO con un filtro por posición; comparar bajo resolución, área cubierta y estímulo normalizados, no solo por número de nodos.

Para una **mancha circular real en el plano** calcular siempre `\rho_{q,r}(t)=\sqrt{(x_{q,r}-x_c(t))^2+(y_{q,r}-y_c(t))^2}`, usando distancias euclidianas en unidades espaciales, **no** únicamente el número de anillos hexagonales. Para un campo centro–periferia fenomenológico definir kernels radiales discretos, por ejemplo `G_{\sigma}(i,j)=exp[-|x_i-x_j|^2/(2\sigma^2)]` y luego normalizar cada fila: `K_\sigma(i,j)=G_\sigma(i,j)/\sum_{k\in\mathcal H_R}G_\sigma(i,k)`. Finalmente `S_i^b=\sum_j[K_{\sigma_c}(i,j)-\kappa K_{\sigma_s}(i,j)]u_j^b` con `\sigma_s>\sigma_c`. Esta elección asegura que el filtro anule cambios uniformes si `\kappa=1`, incluso al borde, pero **no** implica células horizontales explícitas. Documentar los efectos de truncar/renormalizar kernels y comparar contra un campo grande para distinguir fronteras del fenómeno.

**Ventajas:** seis direcciones vecinales equivalentes en una retícula triangular ideal, anillos naturales para la lectura pedagógica, muestreo de discos con menor privilegio de ejes cartesianos que una retícula cuadrada de cuatro vecinos. **Limitaciones:** persiste simetría discreta de seis direcciones (no isotropía continua), y una retícula perfectamente periódica no reproduce las irregularidades ni las densidades variables del mosaico retinal. Un patrón hexagonal de fotorreceptores **no** determina automáticamente el grafo químico real de células horizontales, bipolares o amacrinas. Más adelante podría utilizarse una nube de puntos obtenida de datos reales y vecindad de Voronoi/Delaunay sin cambiar el contrato funcional de M0.

**Comparaciones y pruebas necesarias antes de elegirla definitivamente:**

1. Ejecutar el mismo disco, anillo y barra móvil sobre las retículas **cuadrada** y **hexagonal**, igualando escala física/espacial, tamaño de soporte y parámetros. No comparar una cuadrícula de 49 posiciones con 61 como si fueran la misma resolución sin controlar densidad y área.
2. Probar equivalencia numérica bajo rotaciones de `60°` en una región hexagonal simétrica ideal; estudiar también ángulos intermedios para medir cualquier sesgo de las seis direcciones de la malla.
3. Probar el fondo uniforme, el campo centro–periferia y todos los nodos cercanos al borde para asegurar que una falta de vecinos no introduzca contraste ficticio.
4. Mantener **separadas** la geometría de posiciones, el grafo de procesamiento (pesos/distancias de las conexiones) y el mecanismo fisiológico (M0 y futuras horizontales). Una posición a distancia `a` no significa automáticamente una sinapsis.
5. Medir sensibilidad a pequeñas perturbaciones aleatorias de posiciones (manteniendo identidad y condiciones de borde) para determinar cuánto depende la selectividad del orden perfecto de la malla.

**Motivación biológica pública:** [Sawides, de Castro y Burns (2017), *The organization of the cone photoreceptor mosaic measured in the living human retina*](https://pmc.ncbi.nlm.nih.gov/articles/PMC5290289/), detecta tendencia al empaquetamiento hexagonal y anisotropías locales; [*The Distribution of Cones in the Primate Retina*](https://www.ncbi.nlm.nih.gov/books/NBK235556/) observa islas de organización triangular y defectos en la regularidad. [Webvision, *The Architecture of the Human Fovea*](https://www.webvision.pitt.edu/book/part-ii-anatomy-and-physiology-of-the-retina/the-architecture-of-the-human-fovea/) documenta una organización triangular compacta no perfectamente cristalina.

**Estado de decisión:** alternativa geométrica prioritaria **propuesta**, todavía no aprobada como sustitución definitiva de la cuadrícula 7×7. Se debe demostrar su utilidad con controles de simetría y robustez antes de implementarla en M1-C.

## 7. Observables cuantitativos

Para el detector de derecha, comparar **el mismo detector** ante `v=+|v|` y `v=-|v|` sobre la misma ventana temporal completa, con respuesta `R≥0`:

```math
Q_{pref}=\int_{t_0}^{t_1} R_{\rightarrow}(t;+|v|)\,dt,\qquad
Q_{null}=\int_{t_0}^{t_1}R_{\rightarrow}(t;-|v|)\,dt.
```

```math
DSI=(Q_{pref}-Q_{null})/(Q_{pref}+Q_{null}),
\qquad Q_{pref}+Q_{null}>0.
```

Si ambas integrales son cero, reportar **DSI indefinido**, nunca DSI = 0 por conveniencia. Reportar siempre `Q_pref`, `Q_null`, `DSI`, máximos, retrasos y velocidad. DSI cerca de uno con respuestas ínfimas no constituye evidencia suficiente de un detector útil.

### Predicciones y controles negativos obligatorios

| Prueba | Criterio |
|---|---|
| Contraste local M0 | Incremento: cono ↓, ON ↑, OFF ↓; decremento opuesto |
| Centro–periferia en 1D | Respuesta central frente a periferia de signo opuesto en la **lectura S**; no atribuir este efecto a `V_b` M0 |
| Fondo constante | `u=0`, `a=0`, `y=0` y ninguna activación |
| Iluminación uniforme, κ=1 | `S=0` para el contraste uniforme, incluso al comprobar posiciones cercanas al borde con la convención elegida |
| Filtro temporal ausente | `c_i^→=c_i^←` idénticos para el mismo `a_i` |
| Reflejar la trayectoria | Preferencia invertida por simetría, con mismos parámetros |
| Umbral excesivo | Ninguna respuesta; DSI debe reportarse indefinido |
| Variar velocidad | Máximos y coincidencias cambian; no asumir una velocidad óptima universal |
| Convergencia numérica | Reducir paso/tolerancias no debe alterar signo o magnitudes relevantes |
| Fronteras y dominio | La dirección no debe determinarse por tiempos de entrada/salida diferentes |
| 2D: rotación/simetría | Un campo radial aislado no tiene dirección preferida sin asimetría de procesamiento |

No usar una validación que únicamente verifique que una gráfica se generó. Comprobar matemáticamente invariantes, simetrías, dimensiones y controles con/sin widgets. Los resultados experimentales deberán etiquetarse como **simulación no calibrada**.

## 8. Contrato de software (propuesta, sin código todavía)

**Entorno vigente:** Python ≥3.11; NumPy, SciPy (`solve_ivp`), Matplotlib, JupyterLab, ipywidgets opcional, pytest y nbclient. No añadir PyTorch, Brian2, NEURON ni una infraestructura de grafos pesada para un problema que al inicio tiene veinte EDO.

**Dependencia:** M1 se **implementará después** de revisar/integrar el [PR #8](https://github.com/EduardoLinceGomez/Neurofisiologia/pull/8), o en una rama explícitamente basada en ese PR si permanece en borrador; jamás copiar sus ecuaciones a otros módulos. Esta especificación documental es independiente y se ramifica desde `main`.

Estructura tentativa:

```text
src/neurofisiologia/
    retina_on_off.py                     # M0 existente; conservar
    retina_movimiento/
        estimulos.py                      # Barras, manchas, anillos y protocolos
        poblacion.py                      # Integración espacial vectorizada de M0
        campos_receptivos.py              # Lectura fenomenológica centro–periferia
        detectores.py                     # Filtros temporales y coincidencia local
        simulacion.py                     # Integrador, estados, metadatos
        analisis.py                       # DSI y pruebas cuantitativas
        figuras.py                        # Animación y gráficos sin nuevas EDO
notebooks/
    04_retina_espacial_y_direccion.ipynb   # Lección progresiva, sin duplicar RHS
tests/
    test_retina_espacial_m1.py
docs/
    especificacion_m1_centro_periferia_direccion.md
```

API deseada `simulate_m1(times_ms, grid, stimulus, m0_parameters, spatial_parameters, detector_parameters)`; devolución explícita de `L(x,t)`, `V_C/ON/OFF`, `r`, `g_ON/OFF`, `u`, `S`, `a`, `y`, coincidencias locales, `R^→/←` y métricas. Las figuras toman resultados ya calculados, no reintegran las EDO. Tipos/docstrings en español, unidades y supuestos visibles.

**Visualización pedagógica:** panel sincronizado de estímulo en espacio-tiempo, voltajes ON/OFF por posición, mapa de campo centro–periferia, coincidencias locales y respuestas direccionales. Controles principales de velocidad, `τ_d`, `κ`, `θ` y tamaño espacial, con referencia canónica fija. Navegación de pasos y alternativa Python sin widgets. Empezar por 1D y aumentar complejidad solo después de validar las predicciones.

El repo mantiene protegido `Bibliografia/`; consultar fuentes públicas y enlazarlas sin incorporar PDF/imágenes de terceros, salvo autorización explícita, y no modificar material privado.

## 9. Referencias y límites de atribución

**Fisiología de centro–periferia, fuentes públicas:**

- Kolb, *How the Retina Works*, [Webvision](https://www.ncbi.nlm.nih.gov/books/NBK610611/): figura 9 y texto sobre células horizontales y respuesta del entorno; figura 10 sobre ganglionares ON/OFF-centro.
- Nelson y Connaughton, [*Bipolar Cell Pathways in the Vertebrate Retina*](https://www.webvision.pitt.edu/book/part-v-phototransduction-in-rods-and-cones/bipolar-cell-pathways-in-the-vertebrate-retina/): registros de respuestas al centro y entorno en bipolares.
- Dacey et al. (2000), [*Center surround receptive field structure of cone bipolar cells in primate retina*](https://doi.org/10.1016/S0042-6989(00)00039-0): campos medidos en bipolares de macaco, ajustes por diferencia de gaussianas.
- OpenStax, [*Visual Processing Begins in Bipolar, Horizontal, Amacrine and Ganglion Cells*, §6.3](https://openstax.org/books/introduction-behavioral-neuroscience/pages/6-3-visual-processing-begins-in-bipolar-horizontal-amacrine-and-ganglion-cells): figura 6.14 y esquemas de centro–periferia.
- [*Realistic retinal modeling unravels the differential role of excitation and inhibition to starburst amacrine cells in direction selectivity*](https://pmc.ncbi.nlm.nih.gov/articles/PMC8754344/): ejemplo de modelación de red espacial 2D más mecanística, que **no** se implementa en M1.

**Atribución cuidadosa:** las relaciones `S_C`, `K_c-K_s`, filtros `y_i`, umbral `θ`, parámetros de grilla y su combinación son **hipótesis y propuestas de la herramienta**, no ecuaciones copiadas ni parámetros ajustados a esos estudios. La literatura justifica estudiar señal ON/OFF, periferia antagonista y retardo/dirección, pero no establece por sí sola la elección cuantitativa de este detector M1.

## 10. Puntos científicos a discutir antes de implementar

1. ¿Usar **solo** ON para una mancha brillante y OFF para una oscura en M1-B, o comparar ambas vías en paralelo? Primera opción reduce EDO, segunda permite ver borde frontal/trasero.
2. ¿El primer experimento se limita a contraste espacial fenomenológico, o conviene adelantar una célula horizontal efectiva? Recomendación: distinguir ambos modelos y no añadir horizontal hasta poder interpretar el filtro.
3. ¿Hacemos los experimentos centro–anillo en M1-C simultáneamente con movimiento 2D, o validamos el centro–periferia 2D primero? Recomendación: validar primero el patrón estático y la simetría.
4. ¿Qué variables son experimentalmente observables y cuáles son únicamente latentes/ilustrativas? Documentar antes de cualquier calibración.

**No crear ni fusionar código hasta revisar este diseño.** Los PR #6, #8 y #9 son trabajos independientes; no mezclarlos por conveniencia. Esta especificación debe permanecer revisable y versionada como texto de planificación.

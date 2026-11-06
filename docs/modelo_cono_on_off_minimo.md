# M0: un cono y dos bipolares con respuestas graduadas

M0 responde a una pregunta: **¿cómo una misma reducción de glutamato produce
una despolarización ON y una hiperpolarización OFF?** La diferencia está en la
apertura postsináptica, no en multiplicar un voltaje por −1. Sigue el
[notebook 03](../notebooks/03_cono_bipolares_on_off.ipynb) para predecir, simular
las intervenciones y contrastar esta deducción.

## 1. Fenómeno, variables y límites

Una despolarización significa que el potencial interior respecto al exterior
**aumenta**, por ejemplo de −48 a −44 mV; no necesita hacerse positivo.
Hiperpolarizar es disminuirlo. Una respuesta graduada puede variar continuamente
con el estímulo, sin umbral de disparo ni potencial de acción.

El cono y las dos bipolares son **tres células distintas**, cada una representada
por un solo compartimento eléctrico. La conexión es química. No existe una
conductancia axial que transporte corriente directamente del cono a la bipolar.
El bastón O–I–T de los notebooks 01/02 sigue siendo otro experimento: allí sí hay
acoplamiento axial entre tres regiones de la misma célula.

La figura 6.15 de Sterling y Demb motiva la separación respecto a un fondo; la
página 251 distingue los receptores. La referencia, su alcance y la evidencia
posterior sobre TRPM1 se detallan en [fuentes](referencias_cono_on_off.md).
M0 selecciona solo el tramo cono→bipolares y **no reproduce la figura completa**,
que incluye elementos fuera de nuestro alcance. Los diagramas del notebook son
originales y no están a escala.

| Símbolo | Significado | Unidad interna |
| --- | --- | --- |
| t | Tiempo | ms |
| L, L0 | Iluminación relativa y fondo positivo | Adimensional; sin irradiancia calibrada |
| V_C, V_ON, V_OFF | Potenciales de membrana | mV |
| C_j | Capacitancia total de una célula | pF |
| g_L,j, g_syn,j | Conductancias totales | nS |
| E_j, E_syn,j | Potenciales de reversión efectivos | mV |
| I_foto | Variación efectiva de corriente entrante | pA |
| k_L | Ganancia luz→variación de corriente | pA por unidad L |
| r | Fracción normalizada de liberación | Adimensional; no concentración |

La convención es **corriente entrante positiva**. Se comprueba dimensionalmente
`pF·mV/ms=pA` y `nS·mV=pA`. No usamos densidades de conductancia ni parámetros
de bastones de sapo como calibración de conos.

## 2. Construir primero el cono

La membrana almacena carga. Si la corriente entrante neta es positiva, V sube;
si es negativa, V baja. Una fuga conduce hacia su reversión E_C:

$$
C_C\dot V_C=-g_{L,C}(V_C-E_C)+I_{\rm foto}(t),\qquad
I_{\rm foto}(t)=-k_L[L(t)-L_0].
$$

En el fondo, la **variación** de corriente es cero. Esto no significa ausencia
de corriente oscura real: la actividad basal no resuelta queda absorbida en el
reposo efectivo. Para más luz, la variación entrante es negativa; para menos
luz es positiva. La luz no se inyecta como carga eléctrica.

Si L permanece constante, el equilibrio es
$V_C^\infty=E_C-k_L(L-L_0)/g_{L,C}$, y la constante de tiempo es
$\tau_C=C_C/g_{L,C}$. Desde t_a, la solución RC es
$V_C(t)=V_C^\infty+[V_C(t_a)-V_C^\infty]e^{-(t-t_a)/\tau_C}$.
Esta expresión sirve como comprobación independiente del integrador.

## 3. Del voltaje a la liberación

Se adopta la hipótesis algebraica del Issue #7:

$$
r(V_C)=\frac{1}{1+\exp[-(V_C-V_{1/2})/s]},\qquad s>0.
$$

Despolarizar aumenta r porque $dr/dV_C=r(1-r)/s>0$. En V_half la fracción es
1/2; s determina la anchura de la transición, en mV. La sigmoide evita salidas
negativas y proporciona una liberación acotada; **su forma y sus valores son
hipótesis ilustrativas**, no ajustes experimentales. La implementación usa
`scipy.special.expit` para evitar desbordamientos; numéricamente puede redondear
r a 0 o 1 en saturación. No hay una cuarta EDO ni un tiempo de liberación añadido.

## 4. Construir la bipolar OFF

La apertura catiónica efectiva OFF crece con el glutamato:

$$
g_{OFF}(r)=g_{OFF,max}r,\qquad
C_{OFF}\dot V_{OFF}=-g_{L,OFF}(V_{OFF}-E_{L,OFF})
 +g_{OFF}(r)(E_{syn,OFF}-V_{OFF}).
$$

La corriente sináptica depende de **conductancia por fuerza impulsora**. Si
E_syn está por encima de V, abrir más canales aporta corriente entrante.
Cuando la luz aumenta, r disminuye y se reduce esa entrada: la fuga puede
predominar y el potencial baja. Eso no requiere abrir un canal inhibitorio.

## 5. Construir la bipolar ON

mGluR6 es un receptor metabotrópico: controla indirectamente canales catiónicos.
No es un resistor negativo. M0 resume la inversión mediante

$$
g_{ON}(r)=g_{ON,max}(1-r),\qquad
C_{ON}\dot V_{ON}=-g_{L,ON}(V_{ON}-E_{L,ON})
 +g_{ON}(r)(E_{syn,ON}-V_{ON}).
$$

Las dos corrientes sinápticas tienen **la misma forma algebraica** y reversión
catiónica. En ON, menos glutamato permite mayor conductancia: aumenta la corriente
entrante y V sube. Representar ON mediante E_syn negativo propio de una sinapsis
inhibitoria de Cl⁻ cambiaría el mecanismo acordado.

## 6. El reposo correcto y la prueba del signo

En L=L0, $V_C^*=E_C$, $r^*=r(E_C)$. Para cada bipolar b:

$$
V_b^*=\frac{g_{L,b}E_{L,b}+g_b(r^*)E_{syn,b}}{g_{L,b}+g_b(r^*)}.
$$

Es una media ponderada por conductancias. Con la sinapsis basal abierta,
inicializar V_b en E_L produce un transitorio artificial incluso con luz
constante. `background_equilibrium` evita ese error. Cada condición modificada
usa su propio reposo; en las figuras se muestran tanto V como ΔV respecto a él.

Para una conductancia fija g:

$$
\frac{dV_b^\infty}{dg}=\frac{g_{L,b}(E_{syn,b}-E_{L,b})}{(g_{L,b}+g)^2}>0.
$$

La desigualdad usa E_syn>E_L, exigida por los parámetros M0. Además,
$dV_C^\infty/dL=-k_L/g_{L,C}<0$. Al componer estas relaciones con
`dr/dV_C>0`, `dg_ON/dr<0` y `dg_OFF/dr>0`, aparecen los signos opuestos.
No se introduce un término ±L en la EDO bipolar ni se cambia el signo de las
trayectorias después de integrarlas. Con parámetros asimétricos los signos se
conservan, pero las dos amplitudes y tiempos **no tienen por qué coincidir**.

| Cambio desde L0 | I_foto | V_C | r | g_ON | g_OFF | V_ON | V_OFF |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Incremento | Negativa | ↓ | ↓ | ↑ | ↓ | ↑ | ↓ |
| Decremento | Positiva | ↑ | ↑ | ↓ | ↑ | ↓ | ↑ |
| Fondo sostenido recuperado | 0 | Reposo | r* | Basal | Basal | Reposo | Reposo |

Las flechas comparan con el equilibrio del fondo, no con cero mV. Al retornar
L a L0, I_foto cambia inmediatamente; los voltajes y r pueden seguir desviados
mientras las membranas se relajan. El canal sináptico es instantáneo respecto a
r en M0, pero la membrana bipolar acumula carga: su máximo puede retrasarse
respecto al extremo del cono. No atribuir ese retraso a vesículas que no modelamos.

## 7. Estabilidad y sensibilidad

Con L constante el sistema es triangular: cono→ON/OFF, sin realimentación.
La Jacobiana tiene diagonal
$-g_{L,C}/C_C$, $-(g_{L,ON}+g_{ON})/C_{ON}$,
$-(g_{L,OFF}+g_{OFF})/C_{OFF}$. Son sus tres autovalores, todos negativos.
El equilibrio es localmente estable; las fugas positivas y las conductancias
acotadas permiten la relajación al fondo. No hay un mecanismo de oscilaciones
regenerativas ni spikes en M0.

Cambia **un parámetro cada vez**, manteniendo L y los demás constantes:

- C: modifica velocidad, sin cambiar equilibrio. Duplicar todas las C duplica
  la escala temporal para un nivel constante; un pulso finito puede alcanzar
  menor amplitud si la respuesta se vuelve más lenta.
- k_L: aumenta el desplazamiento del cono para el mismo contraste. Cerca de la
  saturación de r, la respuesta bipolar no crece proporcionalmente sin límite.
- g_L,C: reduce la ganancia estacionaria del cono y acorta su constante de tiempo.
- g_L de una bipolar: cambia el balance con la sinapsis y su reposo, además del tiempo.
- g_syn,max: cambia reposo, ganancia y tiempo; cero desconecta esa bipolar. Su
  equilibrio queda en E_L y deja de responder a la luz, sin afectar al cono ni
  a la otra rama.

El explorador compara siempre con parámetros canónicos fijos. El selector no
redefine la referencia ni oculta cambios del reposo. Los valores modificados
se imprimen junto a las gráficas, con unidades en los nombres de controles.

## 8. Experimentos A–F y reproducción

A: fondo sin pasos, comprobar RHS≈0. B/C: pasos pareados a L0±0.5.
D: retorno y pulsos sucesivos positivos/negativos. E: anular cada sinapsis por
separado. F: sensibilidad a C, fugas, k_L y máximos sinápticos. El notebook
presenta pregunta, predicción, experimento e interpretación para cada caso.
Las [preguntas razonadas](preguntas_cono_on_off.md) permiten estudiar sin ejecutar.

`LightProtocol` usa niveles absolutos no negativos en intervalos [inicio, fin),
ordenados y no solapados; el fondo fuera de ellos es positivo. `simulate_m0`
segmenta `solve_ivp` en **cada** salto y transporta el voltaje final al intervalo
siguiente. Las muestras de salida no determinan qué estímulos ve el integrador.
Si el estímulo empieza antes de la ventana, se exige un estado inicial explícito:
no se inventa la historia faltante.

```bash
source .venv/bin/activate
python -m pytest -q
python scripts/execute_m0_notebook.py --kernel neurofisiologia
python scripts/verify_m0_controls.py --kernel neurofisiologia
jupyter lab notebooks/03_cono_bipolares_on_off.ipynb
```

No se necesitan dependencias nuevas respecto al laboratorio vigente; ipywidgets
es opcional. Las funciones `compare_light` y `compare_parameter` del notebook
sirven como alternativa Python. Las figuras PNG/SVG y notebooks ejecutados
quedan en `outputs/retina_on_off/`, ignorado.

## 9. Qué datos faltan y qué no se implementa

Para calibrar habría que definir especie y tipo celular; medir iluminación y
adaptación de fondo, fotocorriente y V_C, C y fugas, reversión sináptica,
liberación o un indicador validado y respuestas postsinápticas bajo protocolos
comparables. Harían falta incertidumbres, validación fuera del ajuste y una
conversión de unidades. Un solo trazado de voltaje no identifica todos los
parámetros; corriente y conductancia no son intercambiables.

Luz→corriente es fenomenológica y sin fotosensibilidad espectral ni adaptación.
La liberación es instantánea. mGluR6/TRPM1 se reduce a una dependencia algebraica;
no hay cascada bioquímica, Ca²⁺ ni sinapsis de cinta detallada. Tampoco hay
horizontales, amacrinas, GABA, ganglionares, spikes, cable, geometría cilíndrica,
redes ni compartimentos extra. El mapa de extensiones es una propuesta futura:
**validar M0 → calibrar/añadir cinética si los datos lo exigen → justificar
geometría y conectividad**. Ninguna extensión está implementada en esta entrega.

# Estudiar un bastón: de fisiología a ecuaciones

Estas notas acompañan las etapas 00–15 del
[notebook 02](../notebooks/02_estudio_guiado_baston.ipynb). Puedes leerlas sin
ejecutar código. Usa el [glosario](glosario_neurofisio.md) cuando aparezca un
término nuevo y escribe las [predicciones](preguntas_de_estudio_baston.md)
antes de abrir sus respuestas. La especificación aprobada está en
[el plan](planes/02-estudio-guiado-baston.md).

## Qué objeto se estudia y qué afirmaciones hacemos

Un bastón es un fotorreceptor retinal. O agrupa el segmento externo con pigmento;
I, el segmento interno y cuerpo; T, la terminal. En la célula real la salida es
sináptica; aquí T es solo eléctrica. La agrupación de I no reproduce todas las
fronteras anatómicas. Son regiones de una misma célula, no tres neuronas.
El [esquema anatómico de Webvision, fig. 5](https://www.ncbi.nlm.nih.gov/books/NBK11522/)
ayuda a localizar las regiones; no aporta nuestras capacitancias ni conductancias.

Una **sinapsis** es un sitio de comunicación entre células. En una sinapsis
química, un **neurotransmisor** es una molécula mensajera que actúa sobre
receptores de otra célula. La terminal real del fotorreceptor libera glutamato
para esa comunicación. Estudiar V_T aborda una señal eléctrica previa a esa
salida química; V_T por sí solo no cuantifica la liberación. Las otras células
y esos procesos no están en las EDO. Contexto:
[Phototransduction, Neuroscience](https://www.ncbi.nlm.nih.gov/books/NBK10806/).

En oscuridad existe entrada de cationes. Luz activa rodopsina, transducina y PDE;
disminuye cGMP y se cierran canales CNG. Menos corriente entrante favorece
hiperpolarización. Esa cadena motiva la entrada, pero no se integra en el modelo.
La relación entre luz, cGMP y conductancia se investigó en
[Yau y Nakatani (1985), sapo](https://pubmed.ncbi.nlm.nih.gov/2995816/).
La reducción de corriente oscura se observa también en
[Hagins et al. (1970), rata, resumen](https://pubmed.ncbi.nlm.nih.gov/5439318/).
Estas fuentes de contexto no cambian las cifras de referencia de Baylor.

| Categoría | Ejemplo | Qué permite concluir |
| --- | --- | --- |
| Dato experimental | Célula 1 de sapo: A≈1.2 pA, pico≈2.2 s | Escala de corriente registrada |
| Hipótesis de modelado | O/I/T uniformes, C/g/E ilustrativos, entrada impuesta | Sistema que elegimos estudiar |
| Consecuencia matemática | Corrientes axiales se cancelan, estabilidad y superposición | Propiedad deducida de ese sistema |
| Resultado numérico | Un mínimo o retardo en una malla finita | Aproximación para parámetros e input declarados |

Una figura no cambia de categoría por verse fisiológica. La bibliografía pública
y los localizadores completos están en [referencias](referencias_y_parametros.md).

## Definir V, I, C, g y E antes de usarlos

El potencial de membrana es V_interior−V_exterior; exterior se toma como 0.
V=-40 mV describe una diferencia de potencial, no un flujo de -40 pA.
Corriente es carga por tiempo. Nuestra orientación **entrante positiva** hace
que una corriente neta negativa disminuya V para C positiva.

Capacitancia relaciona carga almacenada y potencial: Q=C V. Conductancia
relaciona corriente y diferencia impulsora. La fuga entrante es
I_L=-g_L(V−E). Si V<E, es positiva y eleva V; si V>E, es negativa y lo reduce.
E anula **esa rama**. El reposo anula **la suma**. Una fuga agregada no identifica
una especie iónica ni una conductancia CNG real.

Unidades totales por región: t ms, V mV, C pF, g nS, I pA. En SI,
10⁻¹² F·10⁻³ V/10⁻³ s=10⁻¹² A y 10⁻⁹ S·10⁻³ V=10⁻¹² A.
Por eso pF·mV/ms=pA, nS·mV=pA y pA/pF=mV/ms.

## Un nodo: conservación y tiempo característico

**Hipótesis:** C constante. Derivar Q=C V da dQ/dt=C dV/dt. Conservación de
carga iguala esa derivada con la corriente neta entrante:

\[
C\dot V=-g_L(V-E)+I(t).
\]

Con I=0, anular la derivada da V*=E. Para u=V−E,
du/dt=−(g_L/C)u. Separar variables e integrar produce
u(t)=u(t₀) exp[−(t−t₀)/τ], donde τ=C/g_L en ms.

Con corriente constante I₀ iniciada en t₀ e inicio V(t₀)=E, el equilibrio nuevo
es V∞=E+I₀/g_L. Restar ese valor y resolver la EDO homogénea produce:

\[
V(t)=E+\frac{I_0}{g_L}[1-e^{-(t-t_0)/\tau}],\qquad t\ge t_0.
\]

Antes del escalón V=E. A una τ, se alcanza 63.2% del desplazamiento. Duplicar C
duplica τ sin cambiar V∞; duplicar g modifica ambas magnitudes. Esta es una
entrada constante **didáctica**. Para una entrada breve, C puede cambiar el máximo
observado: no extrapoles el resultado estacionario al evento fotónico.

## Dos nodos: fijar la orientación una sola vez

Definir J_OI=g_OI(V_O−V_I), positivo O→I, exige que aparezca −J_OI en O y
+J_OI en I. Así:

\[
C_O\dot V_O=-g_{L,O}(V_O-E_O)-J_{OI}+I_{photo},\quad
C_I\dot V_I=-g_{L,I}(V_I-E_I)+J_{OI}.
\]

Si O se vuelve más negativo, J_OI<0: el sentido de corriente positiva real se
invierte respecto del elegido. La corriente entra a O y sale de I. La conexión
se opone a la separación de voltajes; puede restaurar O mientras hace caer I.
Sumar carga cancela J, pero no las fugas ni la entrada.

**Experimento:** mismo evento y mismas C/fugas/E; g_IT=0; comparar g_OI=0
con g_OI=0.10 nS. I aislada permanece en reposo. Al conectar I cambia también
O: la señal no se copia intacta, se redistribuye carga.

## Tres nodos: cada término tiene un lugar

Definir J_IT=g_IT(V_I−V_T), positivo I→T, agrega −J_IT en I y +J_IT en T.
Escribir primero los balances individuales evita ocultar signos en una matriz:

\[
\begin{aligned}
C_O\dot V_O&=-g_{L,O}(V_O-E_O)+g_{OI}(V_I-V_O)+I_{photo},\\
C_I\dot V_I&=-g_{L,I}(V_I-E_I)+g_{OI}(V_O-V_I)+g_{IT}(V_T-V_I),\\
C_T\dot V_T&=-g_{L,T}(V_T-E_T)+g_{IT}(V_I-V_T).
\end{aligned}
\]

Las contribuciones axiales por nodo son (−J_OI, J_OI−J_IT, J_IT); suman cero
antes de dividir por C. Con C distintas, g_OI/C_O y g_OI/C_I difieren: **las
corrientes y conductancias son simétricas**, no necesariamente las tasas de V.

El nodo T almacena carga y tiene fuga, pero no input fotosensible directo.
No tiene una variable de glutamato, Ca²⁺ o spike. Anular cualquiera de las dos
conexiones deja T sin respuesta a un input exclusivo en O si se inicia en reposo.

## Resolver el reposo oscuro

Con I_photo=0 y derivadas nulas, pasar los vecinos al lado izquierdo da:

\[
\begin{aligned}
(g_{L,O}+g_{OI})V_O-g_{OI}V_I&=g_{L,O}E_O,\\
-g_{OI}V_O+(g_{L,I}+g_{OI}+g_{IT})V_I-g_{IT}V_T&=g_{L,I}E_I,\\
-g_{IT}V_I+(g_{L,T}+g_{IT})V_T&=g_{L,T}E_T.
\end{aligned}
\]

Con G_L=diag(g_L), estas ecuaciones son K V_dark=G_L E. E iguales permiten
V_dark=E en todos los nodos. E distintos generan corrientes axiales en V=E,
aunque cada fuga sea cero. El verdadero reposo hace que fuga y axial se compensen.
La fotocorriente representa una **variación** respecto de este fondo idealizado;
no se suma otra corriente oscura a las EDO.

## Conectar el experimento de corriente con una entrada impuesta

La referencia de Baylor es una corriente de segmento externo de sapo. El modelo
usa I_photo(t)=−Σ A_k h(t−t_k). No trata al fotón como carga eléctrica ni calcula
eficiencia cuántica. Cada t_k es un evento efectivo ya generado.

Para u≥0, h=(u/t_p)³ exp[3(1−u/t_p)]; antes h=0. Derivar log h da 3/u−3/t_p,
cero en t_p y decreciente después. h(t_p)=1. A es la magnitud positiva del mínimo
de −A h; t_p=2200 ms no es el instante absoluto del evento. Para un evento en
1000 ms, el pico de corriente ocurre en 3200 ms.

La expresión es fenomenológica de cuatro etapas, no una cadena molecular
identificada. C/g/E ilustrativos convierten esa entrada en **voltajes simulados**.
La referencia experimental no permite deducir por sí sola nueve valores eléctricos.

## Leer voltajes, corrientes y métricas

ΔV=V−V_dark evita confundir nivel absoluto con respuesta. El mínimo de V requiere
dV/dt=0, es decir, **corriente neta cero**; la corriente fotosensible puede seguir
siendo negativa. En recuperación, fuga y axial pueden superar su efecto.
`decompose_currents` muestra esas contribuciones con orientación explícita;
`current_balance` suma el mismo desglose y `rhs` divide por C.

Las métricas son mínimos **muestreados** de ΔV (mV), t_min (ms), diferencias de
t_min respecto de O (ms), y |min ΔV_T|/|min ΔV_O| (sin unidades). Sin
hiperpolarización mayor que 10⁻⁸ mV, no se asigna un instante útil: se usa NaN;
los retrasos indefinidos son None. La transmisión es None sin respuesta O,
o cero si O responde y T no. Una malla gruesa cuantiza los tiempos; una ventana
corta puede truncar el mínimo. Retardo de máximos no equivale a velocidad de
conducción ni a un frente de llegada. El sistema discreto tiene transmisión
continua débil tras el evento, no un tiempo de vuelo modelado.

## Parámetros y experimentos justos

La referencia canónica permanece fija: parámetros iniciales, A=1.2 pA,
t_p=2200 ms, 0.3 eventos/s, semilla 2026 y ventana [1000,11000) ms.
Modificar solo A o membrana mantiene exactamente los tiempos de eventos.
Cambiar tasa o semilla cambia el tren; se muestran **ambas entradas**.
Un resultado individual mezcla efecto paramétrico y variabilidad de realización.

El barrido F7 varía g_OI y g_IT, conserva el resto y colorea |min ΔV_T| en mV.
No es una derivada ni una inferencia de parámetros: es una región evaluada
numéricamente, sin interpolación/extrapolación. Los controles avanzados permiten
cambiar C, g_L y E por región; el equilibrio se recalcula.

## Superposición y Poisson

Con reposo inicial y membrana fija, sumar entradas suma ΔV, porque la ecuación
en desviación es lineal. Dos eventos coincidentes duplican ΔV; no duplican V
absoluto. Fisiológicamente, esta linealidad omite saturación y adaptación.

En una ventana de duración T ms, N~Poisson(λT/1000). Condicionados a N,
los tiempos son uniformes y se ordenan. La tasa λ tiene unidades eventos
efectivos/s; no fotones incidentes por área. N puede ser cero con λ positiva.
Semillas locales reproducen cada realización y no modifican el RNG global.
Usar la misma semilla con tasas diferentes no conserva necesariamente eventos.

F8 muestra una realización y luego una muestra de 12 por tasa, con media y
±1 desviación estándar muestral. La banda mide dispersión, no un intervalo de
confianza ni una curva registrada. Linealidad implica escalamiento de la respuesta
media con λ bajo hipótesis fijas; no garantiza el orden de todas las muestras.

## Estructura lineal, estabilidad y evaluación independiente

Después de deducir cada balance, construir C=diag(C_j) y

\[
K=\begin{pmatrix}g_{L,O}+g_{OI}&-g_{OI}&0\\
-g_{OI}&g_{L,I}+g_{OI}+g_{IT}&-g_{IT}\\
0&-g_{IT}&g_{L,T}+g_{IT}\end{pmatrix}.
\]

Sustituir V=V_dark+u y usar K V_dark=G_L E elimina el fondo:
C du/dt=−K u+e_O I(t). K es simétrica; para x≠0,
xᵀKx=Σg_L,j x_j²+g_OI(x_O−x_I)²+g_IT(x_I−x_T)²>0 por las fugas positivas.
Por ello el equilibrio es único y estable. C⁻¹K es similar a C⁻¹/²KC⁻¹/²,
simétrica definida positiva: sus autovalores son positivos y los modos decaen
con τ_m=1/λ_m. No hay modos autónomos oscilatorios o inestables.

En oscuridad, W=½uᵀCu es una función de Lyapunov y dW/dt=−uᵀKu<0. Esta
energía de desviación eléctrica no representa toda la energía metabólica real.
Con entrada, dW/dt=−uᵀKu+u_O I_photo. La entrada puede perturbar el reposo.
Además, M=−C⁻¹K tiene términos fuera de diagonal no negativos: desde u=0
y entrada no positiva, u(t) no es positiva en ningún nodo. Esto explica el
signo hiperpolarizante del modelo, no calibra su amplitud.

Con M=−C⁻¹K, variación de constantes da:

\[
u(t)=e^{M(t-t_0)}u(t_0)+\int_{t_0}^t e^{M(t-s)}C^{-1}e_O I(s)\,ds.
\]

La identidad es exacta para estas EDO. `variation_of_constants` la evalúa con
`expm` y `quad_vec`, por tanto su curva es numérica; sirve de contraste independiente
de `solve_ivp`. El solver sigue integrando la desviación, con tolerancias originales
y paso interno limitado por t_p/30. `time_ms` es la malla de **salida**, no el
paso interno. Iniciar antes del evento o dar un estado con historia correcta.

## Qué explica cada figura y cómo seguir estudiando

| Figura | Trabajo conceptual | No debe confundirse con |
| --- | --- | --- |
| F1 | Componentes y orientación de referencia | Geometría medida |
| F2 | Evento, kernel y corriente impuesta | Spike o traza digitalizada |
| F3 | V, ΔV, reposo y mínimos | Voltaje experimental calibrado |
| F4 | Suma de contribuciones locales | Identificación de canales iónicos |
| F5 | Signos y balances en un instante seleccionado | Trayectorias de iones |
| F6 | Efecto de conectar nodos, misma entrada | Nuevas neuronas o sinapsis |
| F7 | Región evaluada y métrica física | Ajuste o sensibilidad infinitesimal |
| F8 | Realización frente a dispersión de muestra | Efecto de tasa sin azar |

Explica una predicción fallida consultando su término en la EDO. Cambia una variable,
declara qué conservas, observa medidas, y distingue deducción de resultado particular.
No añadas mecanismos para que una curva «parezca real»: primero identifica qué dato
falta. Saturación, adaptación, canales activos, sinapsis, conos y amacrinas requieren
otras hipótesis y evidencia; quedan fuera de esta etapa.

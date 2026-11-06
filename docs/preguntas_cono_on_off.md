# Preguntas razonadas para M0

Predice antes de mirar las soluciones. Usa el
[notebook 03](../notebooks/03_cono_bipolares_on_off.ipynb) y la
[derivación](modelo_cono_on_off_minimo.md) para contrastar tus respuestas.

## 1. ¿ON significa que la luz está encendida?

<details><summary>Razonamiento</summary>
No: el experimento compara con un fondo L0 positivo. Un paso de 1 a 1.5 y uno
de 1 a 0.5 mantienen luz no negativa, pero son incremento y decremento. ON y
OFF describen el signo de la respuesta al cambio relativo, sin spikes.
</details>

## 2. Una bipolar pasa de −48 a −44 mV. ¿Se despolarizó?

<details><summary>Razonamiento</summary>
Sí: ΔV=+4 mV. Despolarizar no exige cruzar cero. La escala absoluta y la
variación respecto al reposo responden preguntas diferentes; el notebook muestra ambas.
</details>

## 3. ¿Por qué la bipolar ON puede subir si el cono baja?

<details><summary>Razonamiento</summary>
Al bajar V_C, disminuye r. La ley g_ON=gmax(1−r) aumenta la apertura catiónica,
mientras E_syn está por encima de V_ON. Crece la entrada sináptica y V_ON sube.
En OFF, g_OFF=gmax*r disminuye: la fuga pasa a dominar y V_OFF baja. No se
multiplican voltajes por signos opuestos ni se conecta ON a una reversión de Cl⁻.
</details>

## 4. ¿Por qué no iniciar ambas bipolares en −60 mV?

<details><summary>Razonamiento</summary>
Con r*=0.5 y gmax=0.5 nS, g*=0.25 nS. El equilibrio es
(1·(−60)+0.25·0)/(1+0.25)=−48 mV. En −60 mV hay 15 pA sinápticos entrantes
sin fuga compensadora; aparecería una despolarización artificial con L constante.
</details>

## 5. ¿Las corrientes sinápticas de ON y OFF deben tener signos contrarios?

<details><summary>Razonamiento</summary>
No. Con V menor que E_syn ambas pueden ser entrantes positivas. Lo que cambia
es su magnitud relativa a la fuga: aumentar una entrada despolariza y reducirla
puede hiperpolarizar. Hay que sumar corrientes antes de dividir por C.
</details>

## 6. ¿Qué ocurre al volver L a L0?

<details><summary>Razonamiento</summary>
I_foto vuelve inmediatamente a cero, pero V_C continúa desplazado por la carga
capacitiva. r depende de ese voltaje y no del nuevo L directamente. Las bipolares
pueden continuar cambiando brevemente antes de volver a su propio reposo. Es un
retraso de membrana, no evidencia de una cinética química ausente del modelo.
</details>

## 7. ¿Duplicar C reduce la respuesta final?

<details><summary>Razonamiento</summary>
Para un nivel constante sostenido, no cambia el equilibrio, porque C desaparece
cuando dV/dt=0. Sí aumenta el tiempo de aproximación. En un pulso de duración
finita puede reducir el máximo observado: la membrana tiene menos tiempo relativo
para aproximarse al nuevo equilibrio. Distingue máximo de un pulso y equilibrio.
</details>

## 8. ¿Desconectar ON debe alterar el cono o la bipolar OFF?

<details><summary>Razonamiento</summary>
No hay realimentación en M0. Con g_ON,max=0, ON queda en su E_L si se inicializa
correctamente. Cono y OFF siguen su trayectoria. El experimento E prueba esta
especificidad. No es equivalente a anular simultáneamente las dos ramas.
</details>

## 9. ¿Las dos respuestas siempre son imágenes especulares?

<details><summary>Razonamiento</summary>
No. Incluso si las conductancias tienen simetría respecto a r=0.5, la respuesta
de voltaje depende del cociente (g_L E_L+g E_syn)/(g_L+g) y de C/(g_L+g).
Parámetros distintos, saturación y pulsos breves alteran amplitud y tiempo.
Los signos provienen del mecanismo; una simetría exacta no es un requisito.
</details>

## 10. ¿Una gráfica que parece fisiológica demuestra calibración?

<details><summary>Razonamiento</summary>
No. L no tiene unidades ópticas y r no es una concentración medida. Faltan
especie/tipo celular, datos de corriente, voltaje, liberación y conductancia,
incertidumbres y validación fuera del ajuste. Las figuras son simulaciones
ilustrativas. El esquema no permite inferir liberación vesicular, adaptación,
GABA, actividad ganglionar ni un campo receptivo espacial.
</details>

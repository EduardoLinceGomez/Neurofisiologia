# Predicciones, ejercicios y respuestas

Usa estas preguntas antes de ejecutar el [notebook 02](../notebooks/02_estudio_guiado_baston.ipynb).
Escribe signo/tendencia, argumento y confianza antes de mirar cada solución.
Las respuestas están plegadas y se repiten en texto al final como alternativa
para visores que no soporten `<details>`. No requieren biblioteca privada.

## Preguntas por etapa

1. **00–01, célula frente a modelo.** ¿O–I–T son tres neuronas? ¿Qué significa agrupar cuerpo y segmento interno en I?
2. **02, mecanismo.** ¿Por qué una luz puede disminuir una corriente entrante? ¿I_photo<0 significa corriente oscura total saliente?
3. **03, signos.** Calcula fuga con g_L=0.05 nS, V=-45 mV, E=-40 mV. ¿Hacia dónde cambia V?
4. **04, carga y RC.** Deduce el balance desde Q=C V. Con C=20 pF, g_L=0.05 nS e I0=-0.3 pA constante, calcula τ, V∞ y V(t0+τ).
5. **04, transferencia.** Duplica C. ¿Se duplica V∞? ¿La misma conclusión vale para un evento de corriente breve?
6. **05–06, axial.** Con g_OI=0.10 nS, V_O=-45 mV, V_I=-42 mV, calcula J_OI y sus contribuciones por nodo. ¿Se cancelan después de dividir por C distintas?
7. **07, reposo.** Con E diferentes, ¿V=E es reposo? Propón una comprobación con las corrientes.
8. **08, referencia.** Un evento empieza a 1000 ms y t_peak=2200 ms. ¿Cuándo alcanza máximo h? ¿Baylor proporciona C y tres voltajes?
9. **09, métricas.** Si T no responde, ¿qué retardo le asignarías? Distingue transmisión cero de cociente indefinido.
10. **10, interpretación.** En el mínimo de V, ¿I_photo debe ser cero? Explica por qué V puede recuperarse mientras la fotocorriente sigue negativa.
11. **11, conectividad.** ¿Qué ocurre con T si g_IT=0? Conserva otros parámetros y predice F6.
12. **12, sensibilidad.** ¿Qué mide el color de F7? ¿Un mapa demuestra calibración o monotonía universal?
13. **13, linealidad.** Dos eventos coincidentes: ¿se duplica V o ΔV? ¿Qué condiciones deben conservarse?
14. **13, Poisson.** Con λ=0.3 eventos/s durante 10 s, calcula E[N], Var[N] y P[N=0]. ¿La misma semilla elimina variabilidad al cambiar tasa?
15. **14, matrices.** Demuestra K definida positiva. ¿Por qué C⁻¹K tiene autovalores reales aunque no sea simétrica?
16. **14, numérico.** Distingue la identidad de variación de constantes de su evaluación con expm/cuadratura. ¿time_ms es el paso del solver?
17. **15, categorías.** Clasifica A=1.2 pA, C_O=20 pF, cancelación axial y un retardo calculado. ¿Qué mediciones faltarían para calibrar V_T?

<details><summary>Ver respuestas razonadas</summary>

**1.** Son regiones de una célula. I es una agrupación eléctrica; no reconstruye
la anatomía ni representa otras neuronas.

**2.** La señalización real reduce apertura CNG y entrada de cationes. I_photo es
el cambio de esa entrada; un cambio negativo no afirma inversión de todo el fondo.

**3.** −0.05(−45+40)=+0.25 pA. Con C positiva, favorece aumentar V hacia E.

**4.** dQ/dt=C dV/dt es la suma entrante. τ=400 ms; V∞=-46 mV;
V(t0+τ)=-40−6(1−exp(−1))≈-43.793 mV. No es un fotón real.

**5.** τ se duplica a 800 ms, V∞ no cambia. Una entrada breve puede producir
otro máximo porque la capacitancia filtra la historia temporal.

**6.** J_OI=−0.30 pA; O recibe +0.30 e I −0.30 pA. Se cancelan como corrientes.
Al dividir por C_O y C_I distintas, las derivadas no tienen por qué cancelarse.

**7.** En V=E, las fugas son cero pero puede haber corriente axial. Resolver
K V_dark=G_L E y evaluar el desglose comprueba neta cero, no cada rama cero.

**8.** El máximo de h ocurre a 3200 ms absoluto. Baylor aporta corriente de
segmento externo de sapo, no nuestros parámetros eléctricos o tres V calibrados.

**9.** No asignar un retardo; t_min es NaN y el retardo None. Si O responde y T
no, el cociente de amplitudes es cero. Si O no responde, el denominador no
resuelve una amplitud y el cociente es None.

**10.** El mínimo requiere neta cero. Foto negativa puede compensarse con fuga
y axiales positivas. Durante recuperación esas contribuciones pueden dominar.

**11.** T aislada y sin input directo inicia y permanece en su reposo. No se
deduce nada sobre glutamato, porque esa variable no existe.

**12.** |min ΔV_T| en mV en cada combinación evaluada. No identifica parámetros
desde datos ni prueba una ley universal fuera del dominio y condiciones.

**13.** Se duplica ΔV con mismo reposo, membrana y eventos coincidentes.
Duplicar V absoluto desplazaría también el fondo y no describe superposición.

**14.** Media=varianza=3; P[N=0]=exp(−3)≈0.0498. La semilla reproduce cada
escenario, pero al cambiar tasa puede cambiar conteo y secuencia de tiempos.
Una comparación individual no aísla todo el efecto estadístico de tasa.

**15.** xᵀKx=Σg_L,j x_j²+g_OI(x_O−x_I)²+g_IT(x_I−x_T)²>0 para x≠0.
C⁻¹K es similar a C⁻¹/²KC⁻¹/², simétrica definida positiva, con espectro real
positivo. En oscuridad los modos decaen; no son necesariamente C_j/g_L,j.

**16.** La identidad es exacta para el modelo; matrices y cuadratura se evalúan
con aproximaciones flotantes. solve_ivp usa pasos adaptativos internos; time_ms
indica dónde guardar salida. Tolerancia numérica no es incertidumbre biológica.

**17.** A: dato experimental de referencia; C_O: hipótesis ilustrativa;
cancelación: consecuencia matemática; retardo: resultado numérico. Calibrar
requiere mediciones eléctricas apropiadas, geometría/área o parámetros efectivos,
especie y condiciones, e identificación validada; no basta una fotocorriente.

</details>

## Alternativa accesible: soluciones en texto

1. Una célula, tres regiones aproximadas.
2. Cambio negativo de entrada, no inversión obligada del fondo.
3. Fuga +0.25 pA, eleva V.
4. Conservación de carga; τ=400 ms, límite -46 mV, valor a τ≈-43.793 mV.
5. τ cambia; límite constante no. El máximo de un evento breve puede cambiar.
6. J=-0.30 pA; O +0.30, I -0.30. Se conservan corrientes, no suma de dV/dt.
7. Reposo exige suma cero; usar sistema acoplado.
8. Pico a 3200 ms; corriente de sapo no calibra tres voltajes.
9. Retardo indefinido; cociente 0 si solo T nula y None si O nula.
10. El mínimo exige neta cero; recuperación puede coexistir con foto negativa.
11. T aislada permanece en reposo; sin variable de liberación.
12. Barrido de amplitud T en mV; no calibración ni ley universal.
13. Superposición de ΔV, conservando fondo y membrana.
14. Media/varianza 3, probabilidad vacía 0.0498; semilla no elimina el azar.
15. K positiva y similaridad explican modos estables.
16. Identidad exacta, evaluación numérica; malla de salida no es paso interno.
17. Separar dato, hipótesis, consecuencia y cálculo; buscar evidencia faltante.

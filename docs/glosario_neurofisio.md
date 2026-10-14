# Glosario bilingüe para el laboratorio

Las definiciones sirven para interpretar las ecuaciones, no para añadir mecanismos.
Fisiología de contexto: [Webvision, Photoreceptors](https://www.ncbi.nlm.nih.gov/books/NBK11522/),
[Yau y Nakatani, cGMP y conductancia fotosensible](https://pubmed.ncbi.nlm.nih.gov/2995816/).
Datos numéricos y especie de cada referencia: [procedencia](referencias_y_parametros.md).

| Inglés | Español | Significado / unidades / cautela |
| --- | --- | --- |
| Rod photoreceptor | Bastón retinal | Fotorreceptor; nuestro referente cuantitativo es sapo. No trasladar cifras a humanos. |
| Outer segment, OS | Segmento externo, O | Región con discos y pigmento; recibe la variación fotosensible impuesta. |
| Inner segment, IS | Segmento interno, I | Región de soporte; este nodo agrupa también cuerpo y conexión, no toda la anatomía. |
| Synaptic terminal | Terminal sináptica, T | Región de comunicación real; aquí solo hay potencial eléctrico, sin liberación calculada. |
| Phototransduction | Fototransducción | Conversión del evento óptico en cambio eléctrico; aquí se sustituye por una entrada impuesta. |
| Rhodopsin | Rodopsina | Pigmento del bastón; no es una variable del sistema O-I-T. |
| Transducin | Transducina | Proteína de señalización del mecanismo real; no se integra. |
| Phosphodiesterase, PDE | Fosfodiesterasa | Enzima que participa en disminuir cGMP; no una corriente eléctrica. |
| cGMP | GMP cíclico | Mensajero químico, no voltaje; sin concentración dinámica en este modelo. |
| Cyclic nucleotide-gated, CNG | Canal activado por nucleótidos cíclicos | Apertura relacionada con cGMP; la fuga ilustrativa no equivale automáticamente a ese canal. |
| Membrane potential | Potencial de membrana | V_in−V_out, mV. No es corriente ni carga. Exterior = referencia 0. |
| Hyperpolarization | Hiperpolarización | V disminuye respecto del reposo; ΔV<0. No significa que toda corriente de fondo invierta dirección. |
| Depolarization | Despolarización | V aumenta respecto de la referencia previa; no obliga a generar un spike. |
| Inward-positive current | Corriente entrante positiva | Convención de signo del laboratorio; neta negativa reduce V para C>0. pA. |
| Dark current | Corriente oscura | Fondo entrante real en oscuridad. I_photo representa su variación, no su valor absoluto. |
| Photocurrent | Fotocorriente | Puede nombrar cambio de corriente o corriente total según fuente; aquí siempre cambio impuesto, pA. |
| Capacitance | Capacitancia | Q=C V; pF totales por nodo. C mayor requiere más carga para igual ΔV. |
| Conductance | Conductancia | Factor g en corriente proporcional a diferencia de potencial; nS totales, no densidad. |
| Leak current | Corriente de fuga | −g_L(V−E) entrante, pA. Rama agregada restauradora; no identifica una especie iónica. |
| Reversal potential | Potencial de reversión | E en mV que anula una rama; no es necesariamente el reposo. |
| Resting / dark equilibrium | Reposo / equilibrio oscuro | Corriente **neta** cero; V_dark resuelve el sistema acoplado. |
| Axial current | Corriente axial | Intercambio intracelular, pA; J_OI positiva O→I, J_IT positiva I→T. |
| Compartment | Compartimento | Aproximación de una región por un V uniforme; no una neurona distinta. |
| Passive membrane | Membrana pasiva | Modelo sin mecanismos regenerativos dependientes de voltaje; no niega mecanismos reales omitidos. |
| Time constant | Constante de tiempo | τ=C/g_L en ms para nodo aislado; en el trío hay modos colectivos. |
| Effective photon event | Evento fotónico efectivo | Respuesta elemental ya generada en un tiempo t_k; no flujo incidente calibrado ni spike. |
| Impulse-response kernel | Núcleo temporal de respuesta | h adimensional; causal, máximo unitario. A en pA escala −A h. |
| Peak photocurrent time | Tiempo al pico de corriente | t_k+t_peak; distingue evento de máximo y de mínimo del voltaje. ms. |
| Peak latency / lag | Latencia / retardo del máximo | Diferencia entre instantes de mínimos muestreados, ms; no velocidad ni tiempo de vuelo. |
| Attenuation / transmission | Atenuación / transmisión | Cociente \|min ΔV_T\|/\|min ΔV_O\|, sin unidades; no ganancia sináptica. |
| Superposition | Superposición | Suma de entradas produce suma de desviaciones, con misma membrana e inicio en reposo. |
| Poisson rate | Tasa Poisson | λ en eventos efectivos/s; parámetro de distribución, no conteo observado. |
| Realization | Realización | Un tren específico de eventos aleatorios; reproducible con semilla. |
| Seed | Semilla | Define reproducibilidad del generador; no asegura igual tren al cambiar tasa. |
| Standard deviation, SD | Desviación estándar, DE | Dispersión; banda muestral no es intervalo de confianza ni error estándar. |
| Numerical tolerance | Tolerancia numérica | Control del error del integrador; no incertidumbre experimental. |
| Output grid | Malla de salida | Tiempos donde guardar V; diferente del paso interno adaptativo. |
| Sensitivity sweep | Barrido de sensibilidad | Región finita evaluada con métrica y unidades; no identificación paramétrica. |
| Action potential / spike | Potencial de acción | Evento regenerativo; no se genera en este modelo pasivo. |
| Glutamate release | Liberación de glutamato | Proceso sináptico real omitido; V_T no cuantifica esa liberación. |

Si una palabra tiene varios usos, declara el de tu experimento. Una cifra de
«respuesta» sin variable, referencia y unidad no es suficiente para comparar.
